import bpy
import mathutils
import sys
import numpy as np

sys.path.append('.')
from blender import Blender

input_file_path = '/home/luca/projects/phd/LearnDecoder_prj/data/conformal/bunny/b1.obj'

wrapper = Blender()

# wrapper.set_image_size(1900, 1080)
wrapper.set_light_location((1,1,1))     # TODO what is a good position for the light?
wrapper.set_cam_location((0, 0, -0.35))
wrapper.fix_camera_yaw(-3.14)
wrapper.point_camera_to_origin()

wrapper.load_object(input_file_path)

wrapper.render('image.png')
wrapper.render_views_rotating('image', num_view=10, up_axis='Y')

wrapper.remove_objects()
