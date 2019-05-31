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

def adinkra_interface(input_image_directory, output_stl_directory, include_base=False, smooth=True, size=256,
                      scale=0.1):
    """
    Opens an adinkra image at input_image_directory, does image manipulation to prepare it for STL conversion,
        converts the resulting image into an STL mesh, then save it at output_stl_directory

        Images must have a white/transparent background

    :required_parameter input_image_directory: (string) the directory of the image to convert to STL
    :required_parameter output_stl_directory: (string) the directory to save the resulting STL file to
    :optional_parameter include_base: (boolean) decides whether or not to add a base to the STL shape
    :optional_parameter smooth: (boolean) decides whether or not the smooth the image to reduce texture
    :optional_parameter size: (int) decides the length and height of the resulting STL file
    :optional_parameter scale: (float) decides the height scaling of the resulting STL mesh
    """

    print("opening image at " + input_image_directory + "...")
    image_matrix = image2stl.read_image(input_image_directory)

    # needed for color correction; in case cv2 opens the image improperly
    white_pixel = [255, 255, 255]
    whitened_image_matrix = image2stl.convert_transparent_to(image_matrix, white_pixel)

    print("resizing to square the images to (" + str(size) + "x" + str(size) + ")...")
    resized_image = image2stl.convert_to_standard_size(whitened_image_matrix, size)

    print("converting the image to grayscale...")
    grayscaled_image = image2stl.grayscale(resized_image)
    # cv2 cant open the image in grayscale, but I don't want to deal with the data type incompatibility
    # so I wrote a homebrew grayscale function

    if smooth == True:
        print("smoothing out the image...")
        smoothed_image = image2stl.smooth_image(grayscaled_image, 1)
    else: # if smooth != True:
        print("smoothing: Disabled")
        smoothed_image = grayscaled_image

    print("Generating the image negative (assumes the wanted areas are not white)...")
    inverted_image = image2stl.grayscale_negative(smoothed_image)

    # current configuration is to display everything except for white/transparent pixels in print

    if include_base == True:
        print("Adding a base: Enabled")
    else:
        print("Adding a base: Disabled")

    print("Generating the corresponding STL file")

    image2stl.convert_to_stl(inverted_image, output_stl_directory, include_base, scale)

    print("STL file generated and saved at " + output_stl_directory)


def prompt_based_interface():
    """
    An interface that asks for user input to get the necessary parameters

    Usage: python2 adinkra_converter.py
        The interface will then ask you for the parameters
    """

    input_image_directory = raw_input("Enter the directory of the image to be converted here >")
    output_stl_directory = raw_input("Enter the directory to save the resulting STL file at here >")
    user_wants_base = raw_input("Include base [Y/N] >")
    user_wants_smooth = raw_input("Smooth the image [Y/N] >")
    user_specified_size = raw_input("size of the resulting STL file >")
    user_specified_scale = raw_input("height scaling of the resulting STL file >")

    if user_wants_base.lower() == "y" or user_wants_base == "yes":
        include_base = True
    else:
        include_base = False

    if user_wants_smooth.lower() == "y" or user_wants_smooth == "yes":
        include_smooth=True
    else:
        include_smooth = False

    if user_specified_size == "":
        output_size = 256
        print("defaulting to 256 x 256")
    else:
        try:
            output_size = int(user_specified_size)

        except Exception as e:
            print("error: " + str(e))
            print("defaulting to 256 x 256")
            output_size = 256

    adinkra_interface(input_image_directory, output_stl_directory, include_base, include_smooth, output_size)


def cli_interface():
    """
    An interface that utilizes command line parameters to get the necessary parameters

    Usage: python2 adinkra_converter.py [-b/--base True/False] [-g/--smooth True/False]
        [-s/--size dimension] [x/--scale scale] image_directory stl_directory

    example:    python2 adinkra_converter.py images/triangle.png stl/triangle_with_base.stl
                python2 adinkra_converter.py --base=True --smooth=False --size=512 --scale=1.0 images/triangle.png
                    stl/circle.stl
    """

    parser = argparse.ArgumentParser(description="Converts adinkra images into STL files for 3D printing.")

    parser.add_argument("-b", "--base", metavar="T/F", type=str, nargs=1, default=False,
                    help="include base or not [True/False]")
    parser.add_argument("-g", "--smooth", metavar="T/F", type=str, nargs=1, default=True,
                    help="smooth image or not [True/False]")
    parser.add_argument("-s", "--size", metavar="size", type=int, nargs=1, default=256,
                    help="size (length and width) of the STL mesh")
    parser.add_argument("-x", "--scale", metavar="scale", type=float, nargs=1, default=0.1,
                    help="height scaling of the STL mesh")
    parser.add_argument("image_directory", type=str, help="directory of image to convert to STL file")
    parser.add_argument("stl_directory", type=str, help="directory of resulting STL file")

    arg_namespace = parser.parse_args()
    arg_dictionary = vars(arg_namespace)

    user_wants_base = arg_dictionary["base"] # result is in list form of one item
    user_wants_smooth = arg_dictionary["smooth"]
    user_specified_size = arg_dictionary["size"]
    user_specified_scale = arg_dictionary["scale"]
    image_directory = arg_dictionary["image_directory"]
    stl_directory = arg_dictionary["stl_directory"]

    # all parameter arguments are in the form of lists
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

    try:
        size = user_specified_size[0]
        print("Size specified: " + str(size))
    except Exception as e: # size is not specified as an argument
        print("default size: 256")
        size = 256

    try:
        scale = user_specified_scale[0]
    except Exception as e: # scale is not specified as an argument
        scale = 0.1

    if size <= 0:
        print("invalid size: " + str(size))
        print("reverting back to default size: 256")
        size = 256

    if scale <= 0.0:
        print("invalid scale: " + str(scale))
        print("reverting back to default scale: 0.1")
        scale = 0.1

    adinkra_interface(image_directory, stl_directory, include_base, include_smooth, size, scale)


def main():
    """
    adinkra_converter.py

    This script converts Adinkra symbols in the form of jpg/png format and converts it to a 
    3D raised projection in STL format.
    
    Example usage: python2 adinkra_converter.py --base=True --smooth=True --size=1024 --scale=1.0
                        ./sample/images/circle.png ./sample/stl/circle_with_base.stl
    
    There is also a fallback interface that allows the user to manually enter in parameter values.
    It's activated with no parameter options
    and can be enabled by uncommenting 'fallback_interface=True' above

    To use this, simply invoke: python2 adinkra_converter.py
    """

    if fallback_interface == True or len(sys.argv) == 1:
        prompt_based_interface()
    else:
        cli_interface()


if __name__ == "__main__":
    main()
