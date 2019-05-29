# Adinkra_extrusion_converter version 1.0
This project contains routines to convert an Adinkra symbol in jpeg/png format and converts it to an STL file for 3D printing.

Make sure that the image background is either white(#FFFFFF) or transparent.

This can be used for any image, not just Adinkra symbols.

# Requirement
 - Python 2.7
 - Numpy 1.16
 - OpenCV-Python 4.1 (for reading and resizing images)
 - Scipy 1.2 (for scipy.ndimage.gaussian_filter)
 - stl_tools 0.3 (find at https://github.com/thearn/stl_tools)

# Installation
Adinkra_converter can be used as is.

The dependencies may be installed via pip with (This may vary based on your particular system)
```
python -m pip install numpy
python -m pip install opencv-python
python -m pip install scipy
python -m pip install stl_tools
```

# adinkra_converter.py usage examples:
A few examples of using adinkra_converter.py are shown below.\
(NOTE: the use of an STL mesh viewer is recommended.)


on [an image on a circle](sample/images/circle.png?raw=false "circle.png"):

![displayed picture of circle](doc/figures/example_circle.png?raw=true)


with adinkra_converter.py:
`python adinkra_converter.py --base=True sample/images/circle.png sample/stl/circle_with_base.stl`

You should get an STL that looks like this (opened with Open 3D Model Viewer):
![circle mesh with base](doc/figures/circle_with_base.png?raw=true "circle mesh with base")


on [an image of a triangle](sample/images/triangle.png?raw=false "triangle.png"):

![displayed picture of triangle](doc/figures/example_triangle.png?raw=true)


with adinkra_converter.py:
`python adinkra_converter.py --base=False sample/images/triangle.png sample/stl/triangle.stl`


You should get an STL that looks like this (opened with Open 3D Model Viewer):
![triangle mesh with no base](doc/figures/triangle_no_base.png "triangle mesh with no base")
