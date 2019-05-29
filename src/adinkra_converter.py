import image2stl

try:
    import argparse
    import sys
except ImportError as e:
    print(e)
    fallback_interface = True
else:
    fallback_interface = False


# uncomment this if you want to use the prompt based interface
# fallback_interface = True

def adinkra_interface(input_image_directory, output_stl_directory, include_base=False):
    """
    Opens an adinkra image at input_image_directory, does image manipulation to prepare it for STL conversion,
        converts the resulting image into an STL mesh, then save it at output_stl_directory

    :required_parameter input_image_directory: (string) the directory of the image to convert to STL
    :required_parameter output_stl_directory: (string) the directory to save the resulting STL file to
    :optional_parameter include_base: (boolean) decides whether or not to add a base to the STL shape
    """

    print("opening image at " + input_image_directory + "...")
    image_matrix = image2stl.read_image(input_image_directory)

    # needed for color correction; in case cv2 opens the image improperly
    white_pixel = [255, 255, 255]
    whitened_image_matrix = image2stl.convert_transparent_to(image_matrix, white_pixel)

    print("resizing to square the images...")
    resized_image = image2stl.convert_to_standard_size(whitened_image_matrix)

    print("converting the image to grayscale...")
    grayscaled_image = image2stl.grayscale(resized_image)
    # cv2 cant open the image in grayscale, but I don't want to deal with the data type incompatibility
    # so I wrote a homebrew grayscale function

    print("smoothing out the image...")
    smoothed_image = image2stl.smooth_image(grayscaled_image, 1)

    print("Generating the image negative (assumes the wanted areas are not white)...")
    inverted_image = image2stl.grayscale_negative(smoothed_image)

    # current configuration is to display everything except for white/transparent pixels in print

    if include_base == True:
        print("Adding a base: Enabled")
    else:
        print("Adding a base: Disabled")

    print("Generating the corresponding STL file")

    stl_scale = 0.1
    image2stl.convert_to_stl(inverted_image, output_stl_directory, include_base, output_scale=stl_scale)

    print("STL file generated and saved at " + output_stl_directory)


def prompt_based_interface():
    """
    An interface that asks for user input to get the necessary parameters

    Usage: python2 image2stl.py
        The interface will then ask you for the parameters
    """

    input_image_directory = raw_input("Enter the directory of the image to be converted here >")
    # path of the default test image

    output_stl_directory = raw_input("Enter the directory to save the resulting STL file at here >")
    # path of the default test STL file

    user_wants_base = raw_input("Include base [Y/N] >")

    if user_wants_base.lower() == "y" or user_wants_base == "yes":
        include_base = True
    else:
        include_base = False

    adinkra_interface(image_directory, stl_directory, include_base)


def cli_interface():
    """
    An interface that utilizes command line parameters to get the necessary parameters

    Usage: python2 image2stl.py [-b/--base True/False] image_directory stl_directory

    example:    python2 image2stl.py --base=True images/triangle.png stl/triangle_with_base.stl
                python2 image2stl.py -b False images/circle.png stl/circle.stl
    """

    parser = argparse.ArgumentParser(description="Converts adinkra images into STL files for 3D printing.")

    parser.add_argument("-b", "--base", metavar="T/F", type=str, nargs=1, default=False,
                    help="include base or not [True/False]")
    parser.add_argument("image_directory", type=str, help="directory of image to convert to STL file")
    parser.add_argument("stl_directory", type=str, help="directory of resulting STL file")

    arg_namespace = parser.parse_args()
    arg_dictionary = vars(arg_namespace)

    user_wants_base = arg_dictionary["base"][0] # result is in list form of one item
    image_directory = arg_dictionary["image_directory"]
    stl_directory = arg_dictionary["stl_directory"]

    if user_wants_base.lower() == 't' or user_wants_base.lower() == "true":
        include_base = True
    elif user_wants_base.lower() == 'f' or user_wants_base.lower() == "false":
        include_base = False
    else:
        print("Cannot recognize base parameter. Using default value \'False\'...")
        include_base = False

    adinkra_interface(image_directory, stl_directory, include_base)


def main():
    """
    adinkra_converter.py

    This script converts Adinkra symbols in the form of jpg/png format and converts it to a 
    3D raised projection in STL format.
    
    Example usage: python2 adinkra_converter.py --base=True ./sample/images/circle.png ./sample/stl/circle_with_base.stl
    
    There is also a fallback interface that allows the user to manually enter in parameter values.
    It's not activated normally but can be enabled by uncommenting 'fallback_interface=False' above
    To use this, simply invoke: python2 adinkra_converter.py
    """

    if fallback_interface == True:
        prompt_based_interface()
    else:
        cli_interface()


if __name__ == "__main__":
    main()
