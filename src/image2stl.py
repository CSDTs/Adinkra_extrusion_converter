"""
image2stl.py

This script contains routines to convert images into STL files
This script is not designed to be stand-alone; run the routine at Adinkra_converter.py
The STL mesh is simply a raised projection of the image itself

If you experience any errors, feel free to contact me at
                                                    email: jiruan@umich.edu
                                                    phone: +1-773-280-1417

NOTE: This is written using Python 2.7. Python 2.7 will be going out of support starting Jan 1, 2020.
"""
# TODO: rewrite this into Python 3.x


import numpy as np
import cv2 # Python bindings for OpenCV
from scipy.ndimage import gaussian_filter

# (APACHE License 2.0) STL file conversion library written by thearn
# find it at https://github.com/thearn/stl_tools
import stl_tools


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


def decode_image_stream(data_uri, read_mode=cv2.IMREAD_UNCHANGED):
    """
    Converts a data stream into a pixel matrix.

    :required_parameter data_uri: (str) A string containing image data.
    :optional_parameter read_mode: (constants from cv2) This constants controls
        how to represent the pixels in the image. The constants include but is not limited to:
            cv2.IMREAD_COLOR - represent pixels as an array designating [red, green, blue] channels
            cv2.IMREAD_GRAYSCALE - represent pixels as intensity information
                0.0 being completely black and 1.0 being completely white
            cv2.IMREAD_UNCHANGED - represent pixels as an array designating [red, green, blue, alpha] channels
    :return: (numpy.ndarray) A matrix of pixels.
    """
    image_binary = np.fromstring(data_uri, dtype=np.uint8)
    image_matrix = cv2.imdecode(image_binary, read_mode)

    return image_matrix


def convert_to_standard_size(image_matrix, size=256):
    """
    Resize the image and change the aspect ratio to 1:1.

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels of the image to resize
    :optional_parameter size: (int) The desired size of the output image, in pixels
        The default parameter specifies an output image of 256 x 256

    :return: (numpy.ndarray) A 2D array of pixels representing the resized image
    """

    dimensions = (size, size)
    resized_image_matrix = cv2.resize(image_matrix, dimensions)

    return resized_image_matrix


def remove_white_borders(image_matrix):
    """
    Resize the image to only contain the shape by removing any white borders
    The resulting image should be have the minimum size required to hold all the nonwhite pixels

    :required_parameter image_matrix: (numpy.ndarray) An image, containing a white background and a shape
    :return: (numpy.ndarray) An image with white borders removed
    """

    # TODO: maybe rewrite this so this image only need to turn into grayscale once
    if len(image_matrix.shape) == 3:
        # threshold and contouring only plays nice with cv2.COLOR_BGR2GRAY grayscaling
        cv2_grayscaled_image = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2GRAY)
    else:
        raise TypeError("Image pixels are not representable as [r, g, b] channels."
                        " Check that the image is represented as a colored image.")

    white_grayscale_pixel = 255
    nonwhite_grayscale_threshold = 254

    _, thresh = cv2.threshold(cv2_grayscaled_image, nonwhite_grayscale_threshold, white_grayscale_pixel,
                              cv2.THRESH_BINARY_INV)
    # create binary image where all white pixels become black, and where all nonwhite pixels become white

    contour_list, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # use external contour lines to find rough outermost shape that encapsulates the object

    # the pixel matrix is indexed via (y, x)
    # but the contour points are indexed(x, y)
    extreme_left = image_matrix.shape[1] # y coordinate of leftmost point of shape
    extreme_right = 0 # y coordinate of rightmost point of shape

    extreme_top = image_matrix.shape[0] # x coordinate of topmost point of shape
    extreme_bottom = 0 # x coordinate of bottom-most point of shape

    # go through every point of each vertices of the outermost shape to find the extreme points
    for contour in contour_list:
        for points in contour:
            point_coord = (points[0][0], points[0][1])

            if point_coord[0] <= extreme_left:
                extreme_left = point_coord[0]

            if point_coord[0] >= extreme_right:
                extreme_right = point_coord[0]

            if point_coord[1] <= extreme_top:
                extreme_top = point_coord[1]

            if point_coord[1] >= extreme_bottom:
                extreme_bottom = point_coord[1]

    # assumes the extreme points can be used to build a square image that encapsulates the whole object
    # also assumes the extreme points builds a square that doesn't index out of the image itself
    return image_matrix[extreme_top:extreme_bottom, extreme_left:extreme_right]


def add_white_border(image_matrix, border=100):
    """
    Add a border to all four sides of an image

    :required_parameter image_matrix: (numpy.ndarray) An image without borders
    :optional_parameter border: (int) the border to be added to all four sides of the image, in pixels
                                        default border is 100 px
    :return: (numpy.ndarray) An image with borders added
    """

    # dimensions are in (y, x)
    image_dimensions = image_matrix.shape

    # re-adjust new image dimensions to have borders
    new_image_dimensions = list(image_dimensions)

    # resize dimensions to include the image dimensions plus border on both sides
    new_image_dimensions[0] += 2 * border
    new_image_dimensions[1] += 2 * border

    new_image = np.full(new_image_dimensions, 255) # white background

    # image offsets to place image with borders on all four sides
    # image starts from 1 pixel past border for both x and y
    image_offsets_y = (border + 1, border + image_dimensions[0] + 1)
    image_offsets_x = (border + 1, border + image_dimensions[1] + 1)

    # place image in center
    new_image[image_offsets_y[0]:image_offsets_y[1], image_offsets_x[0]:image_offsets_x[1]] = image_matrix

    return new_image


def grayscale(image_matrix):
    """
    Converts colored images to grayscale
    Only works for RGB or RGBA images

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels representing an image

    :return: (numpy.ndarray) A 2D array of pixels representing a grayscaled image
    """

    if len(image_matrix.shape) < 3:
        print(image_matrix.shape)
        raise TypeError("Image pixels are not representable as an array of channels."
                        " Check that the image is represented as a colored image.")
    elif image_matrix.shape[2] == 4:
        # image is represented as [red, green, blue, alpha]
        # thus, only [red, green, blue] should be included
        image_matrix = image_matrix[:, :, 0:2]

    grayscaled_image = image_matrix.mean(axis=2)  # computes average of [r,g,b] to generate grayscale

    # theoretically can use cv2.IMREAD_GRAYSCALE to just switch to grayscale outright
    # but doing so results in some weird data type incompatibility issue; so just use this grayscale function
    # for now
    #
    # I could also maybe just use cv2.cvtColor to convert to grayscale
    # but why fix it if it works.

    return grayscaled_image


def smooth_image(image_matrix, standard_deviation = 1.0):
    """
    Smooths out images using the Gaussian function

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels representing an image
    :optional_parameter standard_deviation: The standard deviation of the Gaussian function
        The default standard deviation is 1

    :return: (numpy.ndarray) A 2D array of pixels representing a smoothed image
    """

    smoothed_image = gaussian_filter(image_matrix, standard_deviation)

    return smoothed_image


def transparent_to(pixel, pixel_replacement):
    """
    Checks if a pixel is transparent; replaces with a white pixel if so

    :required_parameter pixel: (numpy.ndarray) A 4 element array representing a [r, g, b, a] pixel
    :return: (numpy.ndarray) An array representing a [r, g, b] pixel
    """

    alpha_channel = 3
    transparent = 0

    if pixel[alpha_channel] == transparent:
        return pixel_replacement
    else:
        return pixel[0:3]


def convert_transparent_to(image_matrix, target_pixel=[255,255,255]): # white pixel by default
    """
    Converts all transparent pixels into white pixels
    Only works on [r, g, b, a] pixels

    :required_parameter image_matrix: (numpy.ndarray) a 2D array of pixels of the image to whiten
    :optional_parameter target_pixel: (numpy.ndarray) a [r, g, b] pixel to replace transparent pixels with.
        the default is a white pixel (#FFFFFF)
    :return: (numpy.ndarray) a 2D of pixels representing the whitened image
    """

    whitened_image = image_matrix[:, :, 0:3]
    row_index = 0

    # go through every pixel; turn all transparent pixel to white
    # also remove the alpha channel
    for row in image_matrix:
        column_index = 0

        for pixel in row:
            whitened_image[row_index][column_index] = transparent_to(pixel, target_pixel)
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


def convert_to_stl(image_matrix, output_file_directory, base=False, output_scale=0.1):
    """
    Converts the image matrix into an STL file and save it at output_file_directory
    NOTE: This function currently only supports grayscale

    :required_parameter image_matrix: (numpy.ndarray) A 2D array of pixels representing an image
    :required_parameter output_file_directory: (string) The filename of the resulting STL file
    :optional_parameter output_scale: decides the height scaling of the resulting STL mesh
    :optional_parameter base: (boolean) A boolean value specifying whether or not
        to include a base into the resulting STL file
    """

    make_it_solid = True  # Change this False to make it hollow; True to make the image solid
    exclude_gray_shade_darker_than = 1.0  # Change this to change what colors should be excluded
    # exclude_gray_shade_below = 1.0 should exclude only black pixels

    # this option controls whether or not stl_tools uses the c library
    # toggle this on if said c library causes issues
    python_only = False

    cv2.imwrite("../sample/images/test3.png", image_matrix)

    if base:
        stl_tools.numpy2stl(image_matrix, output_file_directory,
                scale=output_scale,
                solid=make_it_solid,
                force_python=python_only)
    else:
        stl_tools.numpy2stl(image_matrix, output_file_directory,
                scale=output_scale,
                solid=make_it_solid,
                mask_val=exclude_gray_shade_darker_than,
                force_python=python_only)
