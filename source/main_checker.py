
import os
import sys

sys.path.append('.')
from blender_helper import BlenderHelper


up_axis  = 'Z'
num_view = 10

wrapper = BlenderHelper()
wrapper.set_engine('BLENDER_EEVEE')
wrapper.set_light_location((1,1,1))
wrapper.set_cam_location((0, 2.5, 0))
wrapper.fix_camera_yaw(-3.14)
wrapper.point_camera_to_origin()

wrapper.set_view_solid()


path = '../models/b3.obj'

if os.path.isfile(path):
    files_list = [path]
else:
    files_list = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


for file in files_list:

    if file[-3:] != 'obj':
        continue

    wrapper.load_object(file)

    fila_name = file.split('/')[-1]
    fila_name = fila_name[:fila_name.rfind('.')]

    wrapper.attach_checkerboard_texture()
    wrapper.fit_uv_to_bounds()
    wrapper.scale_uv_coords(0.6, 0)
    wrapper.rotate_uv_coords(3.14, 2)
    wrapper.flip_uv(axis='x')
    wrapper.save_uv_layout(image_name=fila_name+'_uv.png')
    wrapper.save_texture_image(fila_name+'_texture.png', image_name='uv_texture')
    wrapper.render_views_rotating(fila_name, num_view=num_view, up_axis=up_axis)

    wrapper.remove_objects()

wrapper.close()

