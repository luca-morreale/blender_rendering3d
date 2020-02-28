
import os
import bpy
import mathutils
import sys
import numpy as np

sys.path.append('.')
from blender import Blender


wrapper = Blender()
wrapper.set_engine('BLENDER_WORKBENCH')
# wrapper.set_image_size(1900, 1080)
wrapper.set_light_location((1,1,1))     # TODO what is a good position for the light?
# wrapper.set_cam_location((0, 0, -0.35))
wrapper.set_cam_location((0, 0, -5.5))
# wrapper.fix_camera_yaw(-3.14)
wrapper.fix_camera_yaw(0)
wrapper.point_camera_to_origin()

path = '/home/luca/projects/phd/LearnDecoder_prj/remote_sabine/workspace/LearnDecoder/visualization/reconstruction_faust_flat_ae_arch-2048-2048-4-2048-2048_wlinear_batch-1_loss-chamfer_opt-sgd_LR-0.1_l2-0.0_reglamda-0.0_1582118407.983123/train/'

if os.path.isfile(path):
    files_list = [path]
else:
    files_list = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


for file in files_list:

    if file[-3:] != 'ply' and file[-3:] != 'obj':
        continue
    if 'mesh' not in file:
        continue

    wrapper.load_object(file)

    fila_name = file.split('/')[-1]
    fila_name = fila_name[:fila_name.rfind('.')]

    wrapper.render_views_rotating(fila_name, num_view=10, up_axis='Y')

    wrapper.remove_objects()

wrapper.close()

