# blender_rendering3d

Set of python scripts useful to render 3D models with blender

## Disclaimer

The code in this repository is meant to help render models in few specific scenarios I needed. Hence it may not cover your need.

## How to run

```
blender empty.blend --python main.py
```
or 
```
blender empty.blend --python main_checker.py
```

## Scripts

#### main.py

Renders a set of images of the input model(s) specified as path variable inside it. As color of the model is used those attached to the vertices.

#### main_checker.py

Similarly to `main.py` renders a set of images, but attach a checkerboard texture to the model. In this case a uv parametrization is necessary. 

## Acknowledgements

Thanks Noam Aigerman for producing the mesh used as example.
