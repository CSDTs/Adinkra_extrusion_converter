"""
This file contains routines to parse and compile data necessary for conversion of Adinkra designs to raised 3D
projections in STL format.

This file also contains the command line interface for Adinkra conversion.

If you experience any errors, feel free to contact me at
                                                    email: jiruan@umich.edu
                                                    phone: +1-773-280-1417
"""

# project dependencies
import image2stl
import log_handler

# system dependencies
import argparse
import sys
import json
import base64


"""
JSON object -> dictionary
JSON array -> list
string -> unicode string
integers -> int or long
floats -> float
boolean -> boolean
null -> None
"""
def text_to_json(text_data):
    """
    Converts json data in string format into their appropriate json format.

    :required_parameter text_data: (str) A data string containing a data object in json-format.
    :return: (json object) A json object containing the relevant data.
    """

    try:
        json_data = json.loads(text_data)
        # may have many types according to the json conversion table
        # but for adinkra, this should always be 'dictionary'

        return json_data
    except Exception as error_msg:
        log_handler.log_write_fderr(sys.stdout, "json error", str(error_msg))


"""
grammar of data uri in EBNF form:
    image_uri = "data:", [parameters], (", ", data)
    parameters = attribute, "=", value, ";" | media_type, ";" | parameters, parameters | parameters, "base64"

attribute, value, and media_type doesn't have a specific structure and depends on the application that parses them.
They are generally alphanumeric.
Here're some examples that the production rules would find valid:
    attribute, "=", value: "charset=utf-8;"
    media_type: "text/plain;"

data also don't have a specific structure, but if "base64" is included as a parameter,
then data will be encoded in base64.

Here's a Wikipedia article regarding its syntax: https://en.wikipedia.org/wiki/Data_URI_scheme#Syntax
"""
def image_uri_parse(image_uri):
    """
    Parses the data uri scheme for data and parameter values.

    :required_parameter image_uri: (str) A string containing a data uri scheme.
    :return: (tuple) A tuple containing the parameter values and the data itself.
                    The tuple is arranged in (parameters, data) format.
                    The parameters are in list form, and the data is in string form.
                    Individual parameters within the parameter list may exist as either a string,
                    or a tuple containing the attribute name and its value in (attribute_name, attribute_value) format.
    """

    data_header = image_uri[0:5] # should contain "data:" if it's a data uri scheme
    data_start = image_uri.find(',', 5) # denotes start of data
    parameter_values = []

    parameter_start = 5  # after "data:"
    parameter_end = image_uri.find(';', parameter_start) # parameters are separated by semicolons

    # parsing for header; header must be "data:"
    if data_header != "data:":
        raise TypeError("Invalid data uri scheme")

    # parsing for parameters separated by ';'
    while parameter_end != -1 and parameter_end < data_start:
        attribute_set = image_uri.find('=', parameter_start, parameter_end)

        if attribute_set != -1:  # consists of "attribute=value;"
            parameter_attribute = image_uri[parameter_start:]
            parameter_value = image_uri[attribute_set + 1:parameter_end]

            parameter_values.append((parameter_attribute, parameter_value))
        else:  # consists of "media_type;"
            parameter_string = image_uri[parameter_start:parameter_end]
            parameter_values.append(parameter_string)

        parameter_start = parameter_end + 1
        parameter_end = image_uri.find(';', parameter_start)

    # parsing the last parameter between ';' and ','
    if parameter_start < data_start:
        parameter_string = image_uri[parameter_start:data_start]
        parameter_values.append(parameter_string)

    # decoding data
    if parameter_values[-1] == "base64":  # most implementations probably use base64
        data_base64 = image_uri[data_start + 1:]
        binary_data = base64.b64decode(data_base64)

        return (parameter_values, binary_data)
    # TODO: add other methods to parse data here if needed
    else:
        raise Exception("Error: unknown data uri encoding")


def compile_adinkra_parameters(json_data):
    """
    Parses the json data for adinkra conversion parameters.
    Fills in with default values if it's not present in the json data.

    :required_parameter json_data: (dictionary) A dictionary containing data parsed from a json object.
    :return: (tuple) A tuple containing necessary parameters for adinkra conversion.
        The tuple format is (image_matrix, output_stl_directory, include_base, smooth, negative, border, size, scale).
        These are arranged in the order of the input parameters for convert_adinkra().
    """

    # default values from adinkra_converter
    scale = 0.1
    size = 256
    border = 100
    negative = False
    smooth = True
    include_base = False

    # no default values; must include
    output_stl_directory = ""
    image_uri = ""

    # grabbing data from request; default values are filled in if they don't exist
    if "scale" in json_data:
        scale = float(json_data["scale"])

    if "size" in json_data:
        size = int(json_data["size"])

    if "border" in json_data:
        border = int(json_data["border"])

    if "negative" in json_data:
        negative = bool(json_data["negative"])

    if "smooth" in json_data:
        smooth = bool(json_data["smooth"])

    if "base" in json_data:
        include_base = bool(json_data["base"])

    # these parameters must exist in the json data
    try:
        output_stl_directory = str(json_data["stl"])
    except Exception as error_msg:
        log_handler.log_write_fderr(sys.stdout, "stl directory error", str(error_msg))

    try:
        image_uri = str(json_data["image"])
    except Exception as error_msg:
        log_handler.log_write_fderr(sys.stdout, "image data error", str(error_msg))

    # parsing image_uri for the image data
    parsed_uri = image_uri_parse(image_uri)
    # do things with the parameters in image_uri if needed here

    image_matrix = image2stl.decode_image_stream(parsed_uri[1])

    # converting the uri data into an image matrix
    return (image_matrix, output_stl_directory, include_base, smooth, negative, border, size, scale)


def convert_adinkra(image_matrix,
                      output_stl_directory,

                      include_base=False,
                      smooth=True,
                      negative=False,
                      border=100,
                      size=256,
                      scale=0.1):
    """
    Opens an adinkra image at input_image_directory, does image manipulation to prepare it for STL conversion,
        converts the resulting image into an STL mesh, then save it at output_stl_directory

        Images must have a white/transparent background

    :required_parameter image_matrix: (numpy.ndarray) the pixel matrix of the image to convert to STL
    :required_parameter output_stl_directory: (string) the directory to save the resulting STL file to
    :optional_parameter include_base: (boolean) decides whether or not to add a base to the STL shape
                                        default value is False
    :optional_parameter negative: (boolean) if this is true, a square is created with a cavity of the image object
                                        default value is False
    :optional_parameter smooth: (boolean) decides whether or not the smooth the image to reduce texture
                                        default value is True
    :optional_parameter border: (int) decides the width of the border on all four sides of the negative image
                                        (only used when the --negative option is specified)
                                        default size is 100px
    :optional_parameter size: (int) decides the length and height of the resulting STL file
                                        default size is 256 x 256px
    :optional_parameter scale: (float) decides the height scaling of the resulting STL mesh
                                        default scaling is 0.1
    """


    # needed for color correction; in case cv2 opens the image improperly
    if image_matrix.shape == 4: # image exists as [r, g, b, a] channels
        white_pixel = [255, 255, 255]
        whitened_image_matrix = image2stl.convert_transparent_to(image_matrix, white_pixel)
    elif image_matrix.shape == 3: #image opened as [r, g, b] channels; no color correction possible
        whitened_image_matrix = image_matrix
    else:
        # for whatever reason, image is opened as other channels; no color
                                    # corrections possible
        whitened_image_matrix = image_matrix

    print("resizing to square the images to (" + str(size) + "x" + str(size) + ")...")
    resized_image = image2stl.convert_to_standard_size(whitened_image_matrix, size)

    if negative==True:
        print("removing white borders...")
        borderless_image = image2stl.remove_white_borders(resized_image)
        # and the image is repositioned in the center with new borders added back in
        print("Re-adding border (size: " + str(border) + ") according to user specification...")
        bordered_image = image2stl.add_white_border(borderless_image, border)
    else: # removing and re-adding borders on a positive model is useless
        bordered_image = resized_image

    print("converting the image to grayscale...")
    grayscaled_image = image2stl.grayscale(bordered_image)
    # cv2 cant open the image in grayscale, but I don't want to deal with the data type incompatibility
    # so I wrote a homebrew grayscale function

    if smooth == True:
        print("smoothing out the image...")
        smoothed_image = image2stl.smooth_image(grayscaled_image, 1)
    else: # keep image quality
        print("smoothing: Disabled")
        smoothed_image = grayscaled_image

    if negative == True:
        print("Image negative: True")
        print("Keeping the image negaitve (assumes that the areas to print are white)...")
        inverted_image = smoothed_image
        # current configuration is to exclude everything that's not white (greater than or equal to 1.0 grayscale)
    else: # generating a positive model as per default
        print("Generating the image negative (assumes the wanted areas are not white)...")
        print("Image negative: False")
        inverted_image = image2stl.grayscale_negative(smoothed_image)
        # current configuration is to display everything except for white/transparent (less than 1.0 in grayscale)
        # pixels in print

    if include_base == True:
        print("Adding a base: Enabled")
    else: # no base
        print("Adding a base: Disabled")

    print("Generating the corresponding STL file")

    image2stl.convert_to_stl(inverted_image, output_stl_directory, include_base, scale)

    print("STL file generated and saved at " + output_stl_directory)


def cli_interface():
    """
    An interface that utilizes command line parameters to get the necessary parameters

    Usage: python2 adinkra_converter.py [-b/--base True/False] [-g/--smooth True/False] [-c/--negative True/False]
        [-p/--border border_size] [-s/--size dimension] [x/--scale scale] image_directory stl_directory


    example:    python2 adinkra_converter.py images/triangle.png stl/triangle_with_base.stl
                python2 adinkra_converter.py --base=True --smooth=False --negative=Falsse
                --size=512 --scale=1.0 images/triangle.png stl/circle.stl
    """

    parser = argparse.ArgumentParser(description="Converts Adinkra images into STL files for 3D printing.")
    parser.add_argument("-b", "--base", metavar="T/F", type=str, nargs=1, default=False,
                    help="include base or not [True/False]")
    parser.add_argument("-g", "--smooth", metavar="T/F", type=str, nargs=1, default=True,
                    help="smooth image or not [True/False]")
    parser.add_argument("-c", "--negative", metavar="T/F", type=str, nargs=1, default=False,
                    help="Generating a negative print instead or not(T/F)")
    parser.add_argument("-p", "--border", metavar="border", type=int, nargs=1, default=100,
                    help=("width of border, in pixels, to add around negative object(only applies when --negative" +
                         " is enabled)"))
    parser.add_argument("-s", "--size", metavar="size", type=int, nargs=1, default=256,
                    help="size, in pixels, (length and width) of the STL mesh")
    parser.add_argument("-x", "--scale", metavar="scale", type=float, nargs=1, default=0.1,
                    help="height scaling of the STL mesh")
    parser.add_argument("image_directory", type=str, help="directory of image to convert to STL file")
    parser.add_argument("stl_directory", type=str, help="directory of resulting STL file")

    arg_namespace = parser.parse_args()
    arg_dictionary = vars(arg_namespace)

    user_wants_base = arg_dictionary["base"] # result is in list form of one item
    user_wants_smooth = arg_dictionary["smooth"]
    user_wants_negative = arg_dictionary["negative"]
    user_specified_border = arg_dictionary["border"]
    user_specified_size = arg_dictionary["size"]
    user_specified_scale = arg_dictionary["scale"]
    image_directory = arg_dictionary["image_directory"]
    stl_directory = arg_dictionary["stl_directory"]

    # all parameter arguments are in the form of lists; otherwise, it means the command line option simply isn't invoked
    if isinstance(user_wants_base, list):
        if user_wants_base[0].lower() == 't' or user_wants_base[0].lower() == "true":
            include_base = True
        elif user_wants_base[0].lower() == 'f' or user_wants_base[0].lower() == "false":
            include_base = False
        else:
            print("Unknown parameter option; using base default value: \'False\'...")
            include_base = False
    else:
        print("Using base default value: \'False\'...")
        include_base = False

    if isinstance(user_wants_smooth, list):
        if user_wants_smooth[0].lower() == 't' or user_wants_smooth[0].lower() == "true":
            include_smooth = True
        elif user_wants_smooth[0].lower() == 'f' or user_wants_smooth[0].lower() == "false":
            include_smooth = False
        else:
            print("Unknown parameter option; using smooth default value: \'True\'...")
            include_smooth = True
    else:
        print("Using smooth default value: \'True\'...")
        include_smooth = True

    if isinstance(user_wants_negative, list):
        if user_wants_negative[0].lower() == 't' or user_wants_negative[0].lower() == "true":
            generate_negative = True
        elif user_wants_negative[0].lower() == 'f' or user_wants_negative[0].lower() == "false":
            generate_negative = False
        else:
            print("Unknown parameter option; using negative default value: \'False\'...")
            generate_negative = False
    else:
        print("Using negative default value: \'False\'...")
        generate_negative = False

    try:
        size = user_specified_size[0]
        print("Size specified: " + str(size))
    except Exception: # size is not specified as an argument
        print("default size: 256")
        size = 256

    if generate_negative == True:
        try:
            border = user_specified_border[0]
            print("border specified: " + str(border))
        except Exception:
            print("default border size: 100")
            border = 100
    else:  # border is useless on a positive model; thus only considered on negatives
        border = 0

    try:
        scale = user_specified_scale[0]
    except Exception: # scale is not specified as an argument
        print("default scale: 0.1")
        scale = 0.1

    if size <= 0:
        print("invalid size: " + str(size))
        print("reverting back to default size: 256")
        size = 256

    if scale <= 0.0:
        print("invalid scale: " + str(scale))
        print("reverting back to default scale: 0.1")
        scale = 0.1

    print("opening image at " + image_directory + "...")
    image_matrix = image2stl.read_image(image_directory)

    convert_adinkra(image_matrix, stl_directory, include_base, include_smooth, generate_negative, border, size, scale)


if __name__ == "__main__":
    cli_interface()
