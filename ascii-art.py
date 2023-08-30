#---------------------------------------------------------------------------------------------
# File: ascii-art.py
# Author: Greg Dolley
# Date: 6/28/2023
# License: see LICENSE file in root directory of project
#
# This Python script can take any color image, no matter how big or complex, and redraw a
# very realistic version of it using only ASCII art.
#---------------------------------------------------------------------------------------------
import argparse
import os
import platform
import sys
import traceback
from math import ceil

from PIL import Image, ImageDraw, ImageFont

#--------------------------------------------------------------------------------------------------
# GLOBALS
#--------------------------------------------------------------------------------------------------
ASCII_CHARS = ["#", "@", "%", "8", "9", "$", "7", "*", "?", "+", "-", ";", ":", ",", ".", " "]
ASCII_WHITE_INDEX = len(ASCII_CHARS)-1
DEFAULT_OUTPUT_FILENAME = "ascii_image"

user_font_file = ""

#--------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS
#--------------------------------------------------------------------------------------------------
def file_exists(filename): return (os.path.isfile(filename) == True)
def dir_exists(dir_name): return (os.path.isdir(dir_name) == True)
def create_dir(dir_name): os.mkdir(dir_name)
def convert_image_to_grayscale(image): return image.convert("L")
def disable_antialiasing(renderer): renderer.fontmode = "1" # turns off anti-aliasing on TT fonts (renderer = ImageDraw object)

#--------------------------------------------------------------------------------------------------
# main() function entry-point
#--------------------------------------------------------------------------------------------------
def main():
    global user_font_file
    
    image, new_image_width, output_filename, user_font_file = get_user_config() # parse command line and query user for input vars
    image = resize(image, new_image_width) # resize image to custom user width (if specified) and adjust image height to compensate for font aspect ratio (see function for details)

    print("Generating ASCII art text string...")

    ascii_img_text = generate_ascii_art(image) # create complete ASCII art version of image as one huge string
    output_text_filename, output_image_filename = get_output_filenames_with_ext(output_filename) # get output file/path names from config

    create_text_file(output_text_filename, ascii_img_text) # save plain text file version of the ASCII art multi-line string
    textfile_to_image(output_text_filename).save(output_image_filename) # convert the text file to an image as if it were a screenshot

    print(f"ASCII art text file generated: {output_text_filename}")
    print(f"Image version of the same file: {output_image_filename}")

    return 0 # return success code

#--------------------------------------------------------------------------------------------------
# SUPPORT FUNCTIONS
#--------------------------------------------------------------------------------------------------
def create_text_file(output_text_filename, text_content):
    dir_name = os.path.dirname(output_text_filename)
    if dir_name != '' and not dir_exists(dir_name): create_dir(dir_name)
    with open(output_text_filename, "w") as f: f.write(text_content) # save the string to a file to check for accuracy  


def get_font_object(show_warnings=True):
    if len(user_font_file) > 0 and file_exists(user_font_file):
        font_filename = user_font_file
    else:
        font_filename = get_monospace_font_filename()

    if show_warnings == True and len(user_font_file) > 0 and not file_exists(user_font_file): print(f'Warning: could not find user-specified font file: "{user_font_file}"; using alternate font: "{font_filename}".')

    try:
        font = ImageFont.truetype(font_filename, size=12)
    except IOError:
        print(f'Could not load font "{font_filename}".')
        raise

    return font


def textfile_to_image(textfile_path):
    print("Creating image version of ASCII text...")
    
    lines = read_all_lines_rstrip(textfile_path) # read all text lines and put into "lines" array (also rstrip any trailing whitespaces)
    font = get_font_object()
    image_height, max_line_height = sum_pixel_height_for_all_lines(lines, font)
    image_width = calc_widest_line_in_pixels(lines, font)
    new_image, renderer = create_grayscale_image_with_renderer(image_width, image_height)
    disable_antialiasing(renderer)
    draw_text_strings_as_graphical_lines(lines, renderer, max_line_height, font)

    return new_image


def generate_ascii_art(input_image):
    greyscale_image = convert_image_to_grayscale(input_image)
    ascii_str = pixels_to_ascii_chars(greyscale_image)
    img_width = greyscale_image.width
    ascii_img_text = ""

    # add line breaks between each line of text
    for i in range(0, len(ascii_str), img_width):
        ascii_img_text += ascii_str[i:i+img_width] + "\n"
    
    return ascii_img_text


def get_output_filenames_with_ext(output_filename):
    fname_data = dict(filename=output_filename, txt_ext="txt", img_ext="png");
    output_text_filename = "{filename}.{txt_ext}".format(**fname_data)
    output_image_filename = "{filename}.{img_ext}".format(**fname_data)

    return output_text_filename, output_image_filename

    
def draw_text_strings_as_graphical_lines(lines, renderer, line_height, font):
    # draw each line of text onto image canvas
    for i, line in enumerate(lines):
        renderer.text((0, int(round(i * line_height))), line, fill=0, font=font)


def prompt_for_image_file():
    path = ""

    while(len(path) == 0):
        path = input("Enter the path to the image file: ").strip()
        if(len(path) == 0): print("Received blank input.")

    return path


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description='Command-line example.')
    parser.add_argument('-o', action='store', dest='output',
                        metavar='FILE',
                        help='Use FILE as output file name (without extension) instead of default (ascii_image.txt/.png)')
    parser.add_argument('-f', action='store', dest='font_file',
                        metavar='FONT_FILE_PATH',
                        help='Use font file FONT_FILE_PATH for ASCII art font instead of default')
    parser.add_argument('-w', action='store', dest='resize_image_width',
                        metavar='RESIZE_IMAGE_PIXEL_WIDTH',
                        help='Resize the input image width to RESIZE_IMAGE_PIXEL_WIDTH pixels before converting to ASCII art (allows you to shrink/grow the input image if it is too big/small)')

    return parser.parse_args()


def get_user_config():
    args = parse_command_line_arguments()
    path = prompt_for_image_file()
    image = Image.open(path)
    new_image_width = int(args.resize_image_width, base=10) if "resize_image_width" in args and args.resize_image_width != None else image.width
    output_filename = args.output if "output" in args and args.output != None else DEFAULT_OUTPUT_FILENAME
    font_file = args.font_file if "font_file" in args and args.font_file!= None else ""
    print(f"FONT FILE: {font_file}")

    return image, new_image_width, output_filename, font_file


def pixels_to_ascii_chars(image):
    pixels = image.getdata()
    ascii_str = ""
    divisor = 255//(len(ASCII_CHARS)-2)+1

    for pixel in pixels:
        # TODO: it would be better if this was a non-linear scale based on the grayscale histogram of the image.
        # Some images get converted and end up too light
        ascii_char = ASCII_CHARS[pixel//divisor] if pixel != 255 else ASCII_CHARS[ASCII_WHITE_INDEX]
        ascii_str += ascii_char
    return ascii_str


def resize(image, new_width):
    if new_width == None: return image
    if new_width <= 0: return image
    
    font_aspect_ratio = calc_font_aspect_ratio()
    image_aspect_ratio = image.height / image.width
    new_height = new_width * image_aspect_ratio # calc new height in pixels based on user specified width (preserving the original image's aspect ratio)

    # The previous line calculated a new height for the input image because the user specified a custom image width (to preserve the original aspect ratio,
    # obviously the height needs to be adjusted accordingly). The line below this comment block also calculates a new image height, but it's doing so in 
    # order to compensate for the ASCII glyph shape not being a perfect square (I think all ASCII chars have more vertical pixels than horizontal ones for 
    # all common latin fonts). So if you didn't adjust the height to take into account that each ASCII "pixel" in the output "ASCII image" is really a 
    # vertical rectangle instead of a perfect square, then you would end up with an image that looked stretched vertically instead of maintaining the 
    # original image's aspect ratio. The next couple paragraphs explain my solution to fix this because I don't think it's obvious from the code.
    # If you expanded the formula right below this comment block, it would look like this:
    #
    # adjusted_height  = 1 / (font_glyph_height / font_glyph_width) * new_height
    #
    # Basically what this formula is saying is: take the height of a glyph and express it as a percentage of its width (for example, if the height
    # is 30, and the width is 15, then the height as a percentage of the width would be 200% (or 2.0; because 30 is 15 (width) * 2.0 = 30, or 15*200% = 30).
    # Then take that number and innvert it (1 / 2.0 = 0.5 or 50%): the result is the percentage that you take from the image height to get the new
    # and reduceed image height that will fit the vertical rectangular glyphs resulting in vertically stretching this "pre-reduced" image height back
    # into the original height we wanted in the first place.
    # 
    # Complete example: take a 200x200 image where the font glyphs are 15x30 (width 15, height 30), like in the previous example, and calculate the 
    # new height: 1/(30/15)*200 = 1/2*200 = 0.5*200 = 100 pixels high. So the input image is converted from 200x200 into 200x100, which is totally 
    # the incorrect aspect ratio, BUT, if you render 200 15-pixel-wide glyphs, and 100 30-pixel-high glyphs, the resulting image dimensions in pixels 
    # will be exactly 200*15 = 3,000 pixels wide and 100*30 = 3000 pixels high; in other words, a new image with the dimensions of 3000x3000 pixels, 
    # which is a 1.0 aspect ratio image, the same as the original 200x200 input image (200/200 = 1.0).
    #
    # FIXME: the above explanation should work like that in theory, and I don't see anything wrong with it. BUT, what's _really_ happening when you
    # run this script is it's generating output images which have aspect ratios that are about 3% off from their original images (it's barely noicable
    # unless you look really closely at the original image and the output image). I think the reason for this slightly incorrect behavior lies in the
    # vertical pixel spacing _between_ each ASCII line in the output image. If you zoom in on any set of two or three lines, you can tell there's some
    # built-in vertical spacing between them, about three pixels or so. Update: I think I just figured out what might be causing this. This file is a 
    # WIP until I confirm my theory is true and fix the issue.
    new_height =  1/font_aspect_ratio*new_height

    return image.resize((new_width.__round__(), new_height.__round__()))


def get_monospace_font_filename():
    operating_system = platform.system()

    if operating_system == "Windows":
        possible_fonts = ["c:/windows/fonts/consola.ttf"]
    elif operating_system == "Linux":
        possible_fonts = ["/usr/share/fonts/truetype/freefont/FreeMono.ttf",
                          "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"]
    elif operating_system == "Darwin": # MacOS
        possible_fonts = ["/System/Library/Fonts/Monaco.ttf"]

    for font_file in possible_fonts:
        if file_exists(font_file) == True:
            return font_file

    raise FileNotFoundError("Can't find a suitable font file for your operating system.")


def create_grayscale_image_with_renderer(image_width, image_height):
    # Remember that grayscale images don't have RGB pixel values - they have
    # a single color channel going from 0 (black) to 255 (white) and all shades
    # of gray in between (from darkest gray of 1 to lightest gray of 254).
    # In Image.new() below, "L" is for a 256-color grayscale palette and 
    # "color=255" specifies the default background color should be white.
    image = Image.new("L", (image_width, image_height), color=255)
    return image, ImageDraw.Draw(image)


def read_all_lines_rstrip(textfile_path):
    with open(textfile_path) as f:
        lines = tuple(line.rstrip() for line in f.readlines())
    return lines


def calc_widest_line_in_pixels(lines, font):
    widest_line = max(lines, key=lambda s: font.getbbox(s)[2])
    max_line_width = font.getbbox(widest_line)[2]
    return int(ceil(max_line_width))


def calc_tallest_line_in_pixels(lines, font):
    tallest_line = max(lines, key=lambda line: font.getbbox(line)[3])
    # took out numer of vertical pixels in the font's descent size from the calculation (testing a theory for more accurate aspect ratio's on the output image)
    return font.getbbox(tallest_line)[3]#+font.getmetrics()[1] # tallest_line + font descent size in # y-pixels


def sum_pixel_height_for_all_lines(lines, font):
    max_line_height = calc_tallest_line_in_pixels(lines, font)
    return int(ceil(max_line_height * len(lines))), max_line_height


def calc_font_aspect_ratio():
    font = get_font_object(False)

    # using the "M" character glyph since traditionally font metrics are calculated based on the "M" box
    Mbox_width = font.getbbox("M")[2]
    Mbox_height = font.getbbox("M")[3]

    return Mbox_height / Mbox_width


def callstack_prompt(from_traceback):
    while True:
        resp = input("Show callstack? (y/n) ").strip()
        if(len(resp) == 0 or resp == "n"): break
        elif(resp == "y"): 
            traceback.print_tb(from_traceback) 
            break
        
        print("Invalid input. Please try again (note: response is case-sensitive).")


if __name__ == '__main__': # prevent this file from getting "module" loaded
    try:
        status = main()

        print("Done.")
        print(f"Exit status code:  {status}")
        
        sys.exit(status)
    except Exception as e:
        print(sys.exc_info()[1])
        callstack_prompt(sys.exc_info()[2])
        sys.exit(-1)
