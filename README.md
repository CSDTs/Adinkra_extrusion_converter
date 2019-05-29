# Adinkra_extrusion_converter version 1.0
This project contains routines to convert an Adinkra symbol in jpeg/png format and converts it to an STL file for 3D printing.

Make sure that the image background is either white(#FFFFFF) or transparent.

This can be used for any image, not just Adinkra symbols.

# Requirement
Python 2.7
Numpy 1.16
OpenCV-Python 4.1 (for reading and resizing images)
Scipy 1.2 (for scipy.ndimage.gaussian_filter)
stl_tools 0.3 (find at https://github.com/thearn/stl_tools)

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
NOTE: the use of an STL mesh viewer is recommended.



# image2stl.py usage examples:
