# ASCII Art Generator

This is a simple Python program (Python 3) that takes an image file and redraws it as ASCII art. It saves the ASCII art as a plain text file and a PNG screenshot of the text (since a PNG can be zoomed in/out smoothly, while a TXT file cannot).

## Installation

This script has a dependency on the PIL library (Python Image Library, also called Pillow). You can use PIP to install it:

```bash
pip install pillow
```

To check if the installation was successful, open the python terminal:

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
>>> import PIL
```

This loads the PIL library, but the terminal will not output any message after you press \<Enter\> (it'll just print another "```>>>``` line"). Now type this next command and hit \<Enter\>:

```python
>>> PIL.__version__
```

This will make Python print the version of the PIL library on the next line:

```python
>>> PIL.__version__
'10.0.1'
>>> |
```

TODO: add command-line examples of running the ASCII art generator...