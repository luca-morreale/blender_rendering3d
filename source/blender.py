import bpy
from mathutils import Vector
import numpy as np



class Blender(object):

    def __init__(self):
        RANDOM_SEED = 1239
        np.random.seed(RANDOM_SEED)
        self.scene = bpy.context.scene

        self.cam = None
        self.light = None
        self.obj_list = []

        self.set_transparent_background()
        self.set_image_size(1800, 1090)

        self.camera_roll  = None
        self.camera_pitch = None
        self.camera_yaw   = None

        self.set_view_solid()
        self.set_color_by_vertex()


    def set_engine(self, engine):
        self.scene.render.engine = engine

    def set_color_by_vertex(self):
        bpy.context.scene.display.shading.color_type = 'VERTEX'

    def set_view_solid(self):
        for area in bpy.context.screen.areas: # iterate through areas in current screen
            if area.type == 'VIEW_3D':
                for space in area.spaces: # iterate through spaces in current VIEW_3D area
                    if space.type == 'VIEW_3D': # check if space is a 3D view
                        space.shading.type = 'SOLID'  # set the viewport shading


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

    def fix_camera_yaw(self, angle):
        self.camera_yaw = angle

    def fix_camera_pitch(self, angle):
        self.camera_pitch = angle

    def fix_camera_roll(self, angle):
        self.camera_roll = angle

    def create_cam(self):
        # Create the camera
        cam_data = bpy.data.cameras.new('camera')
        self.cam = bpy.data.objects.new('camera', cam_data)
        self.scene.collection.objects.link(self.cam)
        self.scene.camera = self.cam

    def set_cam_rotation(self, rotation):
        if type(rotation) != Vector:
            rotation = Vector(tuple(rotation))

        self.cam.rotation_euler = rotation

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

    def set_cam_location(self, location=None):
        if self.cam is None:
            self.create_cam()
        if type(location) != Vector:
            location = Vector(tuple(location))
        self.cam.location = location

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

    def set_image_size(self, x_res, y_res):
        self.scene.render.resolution_x = x_res
        self.scene.render.resolution_y = y_res

    def set_transparent_background(self):
        self.scene.render.image_settings.color_mode = 'RGBA'
        self.scene.render.film_transparent = True

        world = self.scene.world
        world_tree = bpy.data.worlds[world.name].node_tree
        # world_tree_links = world_tree.links
        # environment_node = world_tree.nodes.new("ShaderNodeTexEnvironment")
        # world_output_node = world_tree.nodes.new("ShaderNodeOutputWorld")
        # background_environment_node = world_tree.nodes.new("ShaderNodeBackground")
        background_node = world_tree.nodes.new("ShaderNodeBackground")
        # mix_shader_node = world_tree.nodes.new("ShaderNodeMixShader")
        # light_path_node = world_tree.nodes.new("ShaderNodeLightPath")

        background_node.inputs[0].default_value = (1, 1, 1, 0)

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

    def remove_objects(self):
        for obj in self.obj_list:
            obj.select_set(True)
        bpy.ops.object.delete()
        self.obj_list = []

    ########################################################################

    def close(self):
        bpy.ops.wm.quit_blender()

    ########################################################################
