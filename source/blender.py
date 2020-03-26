
import os
import bpy
import bpy_extras
from mathutils import Vector
from mathutils import Matrix
import numpy as np


class Blender(object):

    def __init__(self):
        RANDOM_SEED = 1239
        np.random.seed(RANDOM_SEED)
        self.scene = bpy.context.scene

        self.cam = None
        self.light = None
        self.obj_list = []
        self.materials = {}

        self.camera_roll  = None
        self.camera_pitch = None
        self.camera_yaw   = None

        self.set_transparent_background()
        self.set_image_size(1800, 1090)

    ########################################################################
    ##                         Close Blender                              ##
    ########################################################################
    def close(self):
        bpy.ops.wm.quit_blender()


    ########################################################################
    ##                            Enigne                                  ##
    ########################################################################
    def set_engine(self, engine):
        self.scene.render.engine = engine

    ########################################################################
    ##                       Color shading type                           ##
    ########################################################################
    def set_color_by_vertex(self):
        bpy.context.scene.display.shading.color_type = 'VERTEX'

    def set_color_by_texture(self):
        bpy.context.scene.display.shading.color_type = 'TEXTURE'

    ########################################################################
    ##                        View shading type                           ##
    ########################################################################
    def set_view_solid(self):
        for area in bpy.context.screen.areas: # iterate through areas in current screen
            if area.type == 'VIEW_3D':
                for space in area.spaces: # iterate through spaces in current VIEW_3D area
                    if space.type == 'VIEW_3D': # check if space is a 3D view
                        space.shading.type = 'SOLID'  # set the viewport shading

    ########################################################################
    ##                             Light                                  ##
    ########################################################################
    def create_light(self):
        # Create a light
        light_data = bpy.data.lights.new('light', type='POINT')
        self.light = bpy.data.objects.new('light', light_data)
        self.scene.collection.objects.link(self.light)

    def set_light_location(self, location):
        if self.light is None:
            self.create_light()

        if type(location) != Vector:
            location = Vector(tuple(location))

        self.light.location = location

    ########################################################################
    ##                            Camera                                  ##
    ########################################################################
    def create_cam(self):
        # Create the camera
        cam_data = bpy.data.cameras.new('camera')
        self.cam = bpy.data.objects.new('camera', cam_data)
        self.scene.collection.objects.link(self.cam)
        self.scene.camera = self.cam

    def set_cam_location(self, location=None):
        if self.cam is None:
            self.create_cam()
        if type(location) != Vector:
            if location is None:
                location = Vector((0.0, 0.0, 0.0))
            location = Vector(tuple(location))
        self.cam.location = location

    def set_cam_rotation(self, rotation):
        if type(rotation) != Vector:
            rotation = Vector(tuple(rotation))

        self.cam.rotation_euler = rotation

    def fix_camera_yaw(self, angle):
        self.camera_yaw = angle

    def fix_camera_pitch(self, angle):
        self.camera_pitch = angle

    def fix_camera_roll(self, angle):
        self.camera_roll = angle

    def point_camera_to_origin(self):
        direction = (Vector((0.0, 0.0, 0.0)) - self.cam.location).normalized()
        euler_direction = direction.to_track_quat('-Z', 'Y').to_euler()

        if self.camera_roll is not None:
            euler_direction[0] = self.camera_roll
        if self.camera_pitch is not None:
            euler_direction[1] = self.camera_pitch
        if self.camera_yaw is not None:
            euler_direction[2] = self.camera_yaw

        self.set_cam_rotation(euler_direction)


    ########################################################################
    ##                             Image                                  ##
    ########################################################################
    def set_image_size(self, x_res, y_res):
        self.scene.render.resolution_x = x_res
        self.scene.render.resolution_y = y_res

    def set_transparent_background(self):
        self.scene.render.image_settings.color_mode = 'RGBA'
        self.scene.render.film_transparent = True

        world = self.scene.world
        world_tree = bpy.data.worlds[world.name].node_tree
        background_node = world_tree.nodes.new("ShaderNodeBackground")

        background_node.inputs[0].default_value = (1, 1, 1, 0)

    ########################################################################
    ##                             Nodes                                  ##
    ########################################################################
    def link_nodes(self, material, inputs, outputs):
        material.node_tree.links.new(inputs, outputs)


    def create_new_material(self, name):
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        self.materials[name] = material

        return material

    def create_texture_node(self, type, material):
        mat_nodes = material.node_tree.nodes
        texture   = mat_nodes.new(type)
        return texture

    def create_new_image(self, name, type):
        bpy.ops.image.new(name=name, generated_type=type)
        image = bpy.data.images[name]
        return image

    def get_shader_inputs(self, material, shader_name):
        mat_nodes = material.node_tree.nodes
        inputs = mat_nodes[shader_name].inputs
        return inputs

    def attach_material_to_object(self, material, ob):
        # Assign it to object
        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = material
        else:
            # no slots
            ob.data.materials.append(material)


    ########################################################################
    ##                          Mesh loading                              ##
    ########################################################################
    def load_object(self, path):
        obj = self.import_file(path)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN")

        self.obj_list.append(obj)

    def import_file(self, filename):
        if filename[-3:] == 'obj':
            bpy.ops.import_scene.obj(filepath=filename)
        elif filename[-3:] == 'ply':
            bpy.ops.import_mesh.ply(filepath=filename)

        obj = bpy.context.scene.objects[-1]
        return obj

    ########################################################################
    ##                          Mesh removal                              ##
    ########################################################################
    def remove_objects(self):
        # remove all objects in the scene
        for obj in self.obj_list:
            obj.select_set(True)
        bpy.ops.object.delete()
        self.obj_list = []

    ########################################################################
    ##                             Object                                 ##
    ########################################################################
    def select_object(self, active_ob):
        if bpy.context.view_layer.objects.active != active_ob:
            bpy.context.view_layer.objects.active = active_ob

    def deselect_all_objects(self):
        self.select_object(None)

    def toggle_object_edit_mode(self):
        bpy.ops.object.editmode_toggle()

    ########################################################################
    ##                                UV                                  ##
    ########################################################################
    def project_uv_to_bounds(self, active_ob):
        self.select_object(active_ob)
        self.toggle_object_edit_mode()
        self.select_all_uv()
        bpy.ops.uv.pack_islands()
        self.deselect_all_uv()
        self.deselect_all_objects()

    def export_uv_layout(self, image_name, active_ob):
        self.select_object(active_ob)
        self.toggle_object_edit_mode()
        bpy.ops.uv.export_layout(filepath=image_name, export_all=True, opacity=0.0)
        self.deselect_all_objects()

    def flip_uv(self, active_ob, axis='x'):
        self.select_object(active_ob)
        self.toggle_object_edit_mode()
        # self.select_all_uv()

        if axis == 'x':
            axis_rotation = (True, False, False)
        elif axis == 'y':
            axis_rotation = (False, True, False)

        bpy.ops.transform.mirror(constraint_axis=axis_rotation)

        # self.deselect_all_uv()
        self.deselect_all_objects()


    def select_all_uv(self):
        bpy.ops.uv.select_all(action='SELECT')

    def deselect_all_uv(self):
        bpy.ops.uv.select_all(action='DESELECT')


    ########################################################################
    ##                          Checkerboard                              ##
    ########################################################################
    def attach_checkerboard_texture(self, checkerboard_type='color', flip_uv=False,
                                    save_texture=False, image_name=None):

        if checkerboard_type == 'color':
            image_type = 'COLOR_GRID'
        else:
            image_type = 'UV_GRID'

        self.set_color_by_texture()

        material  = self.create_new_material('checkerboard_mat')
        texture_node = self.create_texture_node(type='ShaderNodeTexImage', material=material)
        image = self.create_new_image(name='uv_texture', type=image_type)

        texture_node.image = image

        shader_inputs = self.get_shader_inputs(material=material, shader_name='Principled BSDF')

        self.link_nodes(material, shader_inputs['Base Color'], texture_node.outputs["Color"])
        self.attach_material_to_object(material, self.obj_list[-1])

        self.project_uv_to_bounds(self.obj_list[-1])

        if flip_uv:
            self.flip_uv(self.obj_list[-1], axis='x')

        if save_texture:
            filename, file_extension = os.path.splitext(image_name)
            image.save_render(filename + '_texture' + file_extension)
            self.export_uv_layout(image_name, self.obj_list[-1])


    ########################################################################
    ##                          Rendering                                 ##
    ########################################################################
    def render_views_rotating(self, file_prefix, num_view=10, up_axis='Y'):
        rotation_step = 2.0 * np.pi /num_view
        for i in range(num_view):
            bpy.ops.transform.rotate(value=rotation_step, orient_axis=up_axis)
            self.render('{}_{}_{:02}.png'.format(file_prefix, up_axis, i))

    def render(self, filename):
        # render settings
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.filepath = filename
        bpy.ops.render.render(write_still = 1)

    ########################################################################
