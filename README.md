# ASCII Art Generator

This is a simple Python program (Python 3) that takes an image file and redraws it as ASCII art. It saves the ASCII art as a plain text file and a PNG screenshot of the text (since a PNG can be zoomed in/out smoothly, while a TXT file cannot).

## Installation

This script has a dependency on the PIL library (Python Image Library, also called Pillow). You can use PIP to install it:

```bash
pip install pillow
```

To check if the installation was successful, open the Python console by running the following command:

```bash
python3
```

This will drop you into the Python3 iteractive console and will look similar to this:

```bash
Python 3.10.6 (main, Nov 14 2022, 16:10:14) [GCC 11.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

Now type the following two commands:

```python
import PIL
```

This loads the PIL library, but the terminal will not output any message after you press \<Enter\> (it'll just print another "```>>>```" line). Now type this next command and hit \<Enter\>:

```python
PIL.__version__
```

This will make Python print the version of the PIL library you have installed:

```python
>>> PIL.__version__
'10.0.1'
>>> |
```

To close the Python console, type this line of code and hit \<Enter\>:

```python
exit()
```

## Usage

To run the generator with default settings, simply use the ```python3``` command to run the ```ascii-art.py``` script from the root directory:
 
```bash
python3 ./ascii-art.py
```

The script will prompt you for a path to an image file that you want converted to ASCII art:

```bash
~/ascii_art_generator$ python3 ./ascii-art.py
Enter the path to the image file: █
```

You can use your own image file, or use one of the test files in this repo, such as ```face.jpg```. In the latter case, just type "./face.jpg" and hit \<Enter\>. After a couple seconds, if all goes well, the script will complete leaving behind the following status messages:

```bash
Enter the path to the image file: ./face.jpg
Generating ASCII art text string... 
Creating image version of ASCII text...
ASCII art text file generated: ascii_image.txt
Image version of the same file: ascii_image.png
Done.
Exit status code:  0
~/ascii_art_generator$ █
```

In addition, two new files will have been created in your current directory:

1. ```ascii_image.png```
2. ```ascii_image.txt```

The first file, ```ascii_image.png```, is an image rasterizaton of all the ASCII text lines contained in the second file, ```ascii_image.txt```. The reason for putting the ASCII art drawing in an image file rather than just leaving it as plain-text is two-fold:

1. Every text editor/viewer app is free to choose the number of vertical pixels it will use for line spacing. It can vary based on zoom-level and definitely won't be consistent across different apps. Therefore, it's impossible to calculate aspect ratio correction factors when you don't know what the exact line height will be.
2. If you render everything as a raster image, obviously you're in control of line height, spacing, etc. Once rendered, every image editor/viewer app will show that bitmap in exactly the same way, thus eliminating the problem described in point #1.

TODO... WIP..