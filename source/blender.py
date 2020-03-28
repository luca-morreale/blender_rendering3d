
import bpy
from mathutils import Vector
import numpy as np

class BlenderWrapper(object):
    '''
        Low level blender interaction wrapper
    '''

    def __init__(self):
        RANDOM_SEED = 1239
        np.random.seed(RANDOM_SEED)
        self.scene = bpy.context.scene

        self.cam = None
        self.light = None
        self.obj_list = []
        self.materials = {}
        self.nodes     = {}
        self.images    = {}

        self.camera_roll  = None
        self.camera_pitch = None
        self.camera_yaw   = None

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

    ########################################################################
    ##                             Image                                  ##
    ########################################################################
    def set_image_size(self, x_res, y_res):
        self.scene.render.resolution_x = x_res
        self.scene.render.resolution_y = y_res

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

    def create_node(self, name, type, material):
        mat_nodes = material.node_tree.nodes
        node      = mat_nodes.new(type)

        self.nodes[name] = node

        return node

    def create_new_image(self, name, type):
        bpy.ops.image.new(name=name, generated_type=type)
        image = bpy.data.images[name]

        self.images[name] = image

        return image

    def get_shader_inputs(self, material, shader_name):
        mat_nodes = material.node_tree.nodes
        inputs = mat_nodes[shader_name].inputs
        return inputs

    def get_shader_outputs(self, material, shader_name):
        mat_nodes = material.node_tree.nodes
        outputs = mat_nodes[shader_name].outputs
        return outputs

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
    def select_all_uv(self):
        bpy.ops.uv.select_all(action='SELECT')

    def deselect_all_uv(self):
        bpy.ops.uv.select_all(action='DESELECT')


    ########################################################################
    ##                          Rendering                                 ##
    ########################################################################
    def render(self, filename):
        # render settings
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.filepath = filename
        bpy.ops.render.render(write_still = 1)

    ########################################################################
