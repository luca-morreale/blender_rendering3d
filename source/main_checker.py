
import os
import sys

sys.path.append('.')
from blender import Blender


up_axis = 'Y'
num_view = 4

wrapper = Blender()
wrapper.set_engine('CYCLES')
wrapper.set_light_location((1,1,1))
wrapper.set_cam_location((0, 0, -0.5))
wrapper.fix_camera_yaw(-3.14)
wrapper.point_camera_to_origin()

wrapper.set_view_solid()



path = '../models/b3.obj'


if os.path.isfile(path):
    files_list = [path]
else:
    files_list = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


for file in files_list:

    if file[-3:] != 'ply' and file[-3:] != 'obj':
        continue

    wrapper.load_object(file)
    wrapper.attach_checkerboard_texture()

    fila_name = file.split('/')[-1]
    fila_name = fila_name[:fila_name.rfind('.')]

    wrapper.render_views_rotating(fila_name, num_view=num_view, up_axis=up_axis)

    wrapper.remove_objects()

wrapper.close()

