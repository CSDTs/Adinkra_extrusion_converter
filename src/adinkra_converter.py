import image2stl

try: # can your computer parse command line argument?
    import argparse
    import sys
except ImportError as e:
    print(e)
    fallback_interface = True
else:
    fallback_interface = False


# uncomment this if you want to use the prompt based interface
# fallback_interface = True

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
    else: # for whatever reason, image is opened as other(possibly [r, g, b]) channels; no color
                                    # corrections possible
        whitened_image_matrix = image_matrix

    print("resizing to square the images to (" + str(size) + "x" + str(size) + ")...")
    resized_image = image2stl.convert_to_standard_size(whitened_image_matrix, size)

    if negative==True:
        print("removing white borders...")
        borderless_image = image2stl.remove_white_borders(resized_image)
        # and the image is repositioned in the center with new borders added back in
        print("Re-adding border (size: " + str(border) + ") according to user specification...")
        bordered_image = image2stl.add_back_white_border(borderless_image, border)
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

    parser = argparse.ArgumentParser(description="Converts adinkra images into STL files for 3D printing.")
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
        except ErrorMsg:
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
