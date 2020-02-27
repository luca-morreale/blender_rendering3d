import bpy
import mathutils
import sys
import numpy as np

sys.path.append('.')
from utils import set_transparent_background, set_image_resolution
from utils import create_light, set_light_location
from utils import create_cam, set_cam_location, direct_camera_to_point
from utils import render_image, import_file
from utils import get_obj_center, rotate_point


RANDOM_SEED = 1239

np.random.seed(RANDOM_SEED)

scene = bpy.context.scene

input_file_path = '/home/luca/projects/phd/LearnDecoder_prj/data/conformal/bunny/b1.obj'
obj = import_file(scene, bpy, input_file_path)
bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN")
mean = get_obj_center(scene, bpy, obj)


set_transparent_background(scene, bpy)
set_image_resolution(scene, bpy, 1800, 1090)


# TODO what is a good position for the light?
create_light(scene, bpy)
set_light_location(scene, bpy, (1,1,1))

# TODO find a way to get these values easily!
cam = mathutils.Vector((0, 0, -0.35))
create_cam(scene, bpy)
set_cam_location(scene, bpy, cam)
direct_camera_to_point(scene, bpy, cam, mean)


render_image(scene, bpy, 'image.png')


up_axis = 'Y'
for i in range(10):
    bpy.ops.transform.rotate(value=2*3.14/10.0, orient_axis=up_axis)
    render_image(scene, bpy, f'image{up_axis}_{i}.png')

