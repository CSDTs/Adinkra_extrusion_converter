import numpy as np
import cv2 # Python bindings for OpenCV
from scipy.ndimage import gaussian_filter

# (APACHE License 2.0) STL file conversion library written by thearn
# find it at https://github.com/thearn/stl_tools
from stl_tools import numpy2stl

"""
image2stl.py

This script contains routines to convert images into STL files
This script is not designed to be stand-alone; run the routine at adinkra_converter.py
The STL mesh is simply a raised projection of the image itself

If you experience any errors, feel free to contact me at jiruan@umich.edu

NOTE: This is written using Python 2.7. Python 2.7 will be going out of support starting Jan 1, 2020.
TODO: rewrite this into Python 3.x
"""


def read_image(image_directory, read_mode=cv2.IMREAD_UNCHANGED):
    """
    This function reads in an image directory as a string and returns a numpy array of pixels in the image

    :required_parameter image_directory: (String) The path in which the image resides
        The path can be a relative path to this script or an absolute path

    :optional_parameter read_mode: (constants from cv2) This constants controls
        how to represent the pixels in the image. The constants include but is not limited to:
            cv2.IMREAD_COLOR - represent pixels as an array designating [red, green, blue] channels
            cv2.IMREAD_GRAYSCALE - represent pixels as intensity information
                0.0 being completely black and 1.0 being completely white
            cv2.IMREAD_UNCHANGED - represent pixels as an array designating [red, green, blue, alpha] channels

    :return: (numpy.ndarray) an array of pixels representing the opened image
    """

    image_matrix = cv2.imread(image_directory, read_mode)

    if image_matrix is None:  # test if image exists and is read successfully
        error_str = "Cannot find file: " + str(image_directory)
        raise IOError(error_str)

    return image_matrix  # should be a 2d matrix of pixels


def convert_to_standard_size(image_matrix, size=256):
    """
    Resize the images and change the aspect ratio to 1:1.

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels of the image to resize
    :optional_parameter size: (int) The desired size of the output image
        The default parameter specifies an output image of 256 x 256

    :return: (numpy.ndarray) A 2D array of pixels representing the resized image
    """

    dimensions = (size, size)
    resized_image_matrix = cv2.resize(image_matrix, dimensions)

    return resized_image_matrix


def grayscale(image_matrix):
    """
    Converts colored images to grayscale
    Only works for RGB or RGBA images

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels representing an image

    :return: (numpy.ndarray) A 2D array of pixels representing a grayscaled image
    """

    if len(image_matrix.shape) < 3:
        raise TypeError("Image pixels are not representable as an array of channels."
                        " Check that the image is represented as a colored image.")
    elif image_matrix.shape[2] == 4:
        # image is represented as [red, green, blue, alpha]
        # thus, only [red, green, blue] should be included
        image_matrix = image_matrix[:, :, 0:2]

    grayscaled_image = image_matrix.mean(axis=2)  # computes average of [r,g,b] to generate grayscale

    # theoretically can use cv2.IMREAD_GRAYSCALE to just switch to grayscale outright
    # but doing so results in some weird data type incompatibility issue; so juse use the grayscale function
    # for now

    return grayscaled_image


def smooth_image(image_matrix, standard_deviation = 1):
    """
    Smooths out images using the Gaussian function

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels representing an image
    :optional_parameter standard_deviation: The standard deviation of the Gaussian function
        The default standard deviation is 1

    :return: (numpy.ndarray) A 2D array of pixels representing a smoothed image
    """

    smoothed_image = gaussian_filter(image_matrix, standard_deviation)

    return smoothed_image


def transparent_to_white(pixel):
    """
    Checks if a pixel is transparent; replaces with a white pixel if so

    :required_parameter pixel: (numpy.ndarray) A 4 element array representing a [r, g, b, a] pixel
    :return: (numpy.ndarray) An array representing a [r, g, b] pixel
    """

    alpha_channel = 3
    transparent = 0
    white_pixel = np.array([255, 255, 255])

    if pixel[alpha_channel] == transparent:
        return white_pixel
    else:
        return pixel[0:3]


def convert_transparent_to_white(image_matrix):
    """
    Converts all transparent pixels into white pixels
    Only works on [r, g, b, a] pixels

    :required_parameter image_matrix: (numpy.ndarray) a 2D array of pixels of the image to whiten
    :return: (numpy.ndarray) a 2D of pixels representing the whitened image
    """

    whitened_image = image_matrix[:, :, 0:3]
    row_index = 0

    for row in image_matrix:
        column_index = 0

        for pixel in row:
            whitened_image[row_index][column_index] = transparent_to_white(pixel)
            column_index += 1

        row_index += 1

    return whitened_image


def gray_inverse(pixel):
    """
    Inverts the color of the given pixel

    :required_parameter pixel:  A pixel from a grayscaled image

    :return: the inverted color of the pixel in the resulting negative image
    """

    return 255 - pixel


def grayscale_negative(image_matrix):
    """
    Converts the grayscaled image array into its respective negative

    :required_parameter image_matrix: (numpy.ndarray) The desired grayscale image to create a negative of

    :return: The resulting negative image
    """

    negative = np.array([gray_inverse(pixel) for pixel in image_matrix])

    return negative


def convert_to_stl(image_matrix, output_file_directory, base=False):
    """
    Converts the image matrix into an STL file and save it at output_file_directory
    NOTE: This function currently only supports grayscale

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels representing an image
    :required_parameter output_file_directory: (string) The filename of the resulting STL file
	:optional_parameter base: (boolean) A boolean value specifying whether or not
		to include a base into the resulting STL file
    """

    output_scale = 0.1  # Change this to scale the resulting 3D file up or down
    make_it_solid = True  # Change this False to make it hollow; True to make the image solid
    exclude_gray_shade_darker_than = 1.0  # Change this to change what colors should be excluded
    # exclude_gray_shade_below = 1.0 should exclude only black pixels; but I'm not sure

    # this option controls whether or not stl_tools uses the c library
    # toggle this on if said c library causes issues
    python_only = False

    if base:
	    numpy2stl(image_matrix, output_file_directory,
		        scale=output_scale,
				solid=make_it_solid,
				force_python=python_only)
    else:
		numpy2stl(image_matrix, output_file_directory,
				scale=output_scale,
				solid=make_it_solid,
				mask_val=exclude_gray_shade_darker_than,
				force_python=python_only)
