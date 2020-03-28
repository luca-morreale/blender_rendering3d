
import os
import bpy
from mathutils import Vector
import numpy as np

import sys
sys.path.append('.')
from blender import BlenderWrapper


class BlenderHelper(BlenderWrapper):

    def __init__(self):
        super().__init__()

        self.set_transparent_background()
        self.set_image_size(1800, 1090)


    ########################################################################
    ##                            Camera                                  ##
    ########################################################################
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
    def set_transparent_background(self):
        self.scene.render.image_settings.color_mode = 'RGBA'
        self.scene.render.film_transparent = True

        world = self.scene.world
        world_tree = bpy.data.worlds[world.name].node_tree
        background_node = world_tree.nodes.new("ShaderNodeBackground")

        background_node.inputs[0].default_value = (1, 1, 1, 0)

    ########################################################################
    ##                                UV                                  ##
    ########################################################################
    def fit_uv_to_bounds(self, active_ob=None):
        if active_ob is None:
            active_ob = self.obj_list[-1]

        self.select_object(active_ob)
        self.toggle_object_edit_mode()
        self.select_all_uv()
        bpy.ops.uv.pack_islands()
        self.deselect_all_uv()
        self.deselect_all_objects()

    def save_uv_layout(self, image_name, active_ob=None):
        if active_ob is None:
            active_ob = self.obj_list[-1]

        self.select_object(active_ob)
        self.toggle_object_edit_mode()
        bpy.ops.uv.export_layout(filepath=image_name, export_all=True, opacity=0.0)
        self.deselect_all_objects()

    def scale_uv_coords(self, scale, axis, mapping_node_name='mapping'):
        mapping_node = self.nodes[mapping_node_name]
        mapping_node.inputs['Scale'].default_value[axis] = scale

    def rotate_uv_coords(self, rotation, axis, mapping_node_name='mapping'):
        mapping_node = self.nodes[mapping_node_name]
        mapping_node.inputs['Rotation'].default_value[axis] = rotation

    def flip_uv(self, axis='x', active_ob=None):
        if active_ob is None:
            active_ob = self.obj_list[-1]

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

    ########################################################################
    ##                          Checkerboard                              ##
    ########################################################################
    def attach_checkerboard_texture(self, checkerboard_type='color'):

        if checkerboard_type == 'color':
            image_type = 'COLOR_GRID'
        else:
            image_type = 'UV_GRID'

        self.set_color_by_texture()

        material = self.create_new_material('checkerboard_mat')

        texture_node    = self.create_node(name='texture', type='ShaderNodeTexImage', material=material)
        mapping_node    = self.create_node(name='mapping', type='ShaderNodeMapping', material=material)
        text_coord_node = self.create_node(name='texcoord', type='ShaderNodeTexCoord', material=material)

        shader_inputs = self.get_shader_inputs(material=material, shader_name='Principled BSDF')

        self.link_nodes(material, shader_inputs['Base Color'], texture_node.outputs["Color"])
        self.link_nodes(material, text_coord_node.outputs['UV'], mapping_node.inputs['Location'])
        self.link_nodes(material, mapping_node.outputs['Vector'], texture_node.inputs['Vector'])


        mapping_node.vector_type = 'TEXTURE'
        image = self.create_new_image(name='uv_texture', type=image_type)
        texture_node.image = image

        self.attach_material_to_object(material, self.obj_list[-1])

    def save_texture_image(self, filename, image_name='uv_texture'):
        image = self.images[image_name]
        image.save_render(filename)

    ########################################################################
    ##                          Rendering                                 ##
    ########################################################################
    def render_views_rotating(self, file_prefix, num_view=10, up_axis='Y'):
        rotation_step = 2.0 * np.pi /num_view
        for i in range(num_view):
            bpy.ops.transform.rotate(value=rotation_step, orient_axis=up_axis)
            filename = '{}_{}_{:02}.png'.format(file_prefix, up_axis, i)
            self.render(filename)

    ########################################################################
