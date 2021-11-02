import qrcode
import qrcode.image.svg
from argparse import ArgumentParser
import logging
import sys
import os

from svg.path import parse_path
from svg.path.path import Line
from xml.dom import minidom

# Constants
TMP_FILE_SVG = ".tmp.svg"
FORMAT_STRING = "\t\t\tdraw_filled_rect({:.0f}, {:.0f}, {:.0f}, {:.0f});\n"
MAX_WIDTH = 175
MAX_HEIGHT = 175

# Functions


def convert_xml_attr(attr):
    return int(str(attr).replace("mm", ""))


def configure_in_file(result, fileName):
    filedata = str()
    with open(fileName + ".in", 'r') as file:
        filedata = file.read()

    filedata = filedata.replace("@REPLACE_STRING@", result)

    with open(fileName, 'w') as file:
        file.write(filedata)


def find_max_min(rect_tuples):
    min_x = MAX_WIDTH
    min_y = MAX_HEIGHT
    max_x = 0
    max_y = 0
    for it in rect_tuples:
        x = it[0]
        y = it[1]
        if(min_x > x):
            min_x = x
        if(x > max_x):
            max_x = x
        if(min_y > y):
            min_y = y
        if(y > max_y):
            max_y = y
    return tuple((min_x, min_y, max_x, max_y))


def find_width(min_max):
    width_height = tuple((min_max[2] - min_max[0], min_max[3] - min_max[1]))
    if(width_height[0] != width_height[1]):
        logging.error("it's not a square")
        sys.exit(1)
    if(width_height[0] > MAX_WIDTH):
        logging.error("Current width:" + str(width_height[0]) +
                      " more than " + str(MAX_WIDTH))
        sys.exit(1)
    return width_height[0]


# Args
parser = ArgumentParser()
parser.add_argument("-t", "--text", dest="text",
                    help="you text", metavar="TEXT")
args = parser.parse_args()
if not (args.text):
	logging.error("No href specified")
	print(parser.print_help())
	sys.exit(1)

# Main
img = qrcode.make(args.text, image_factory=qrcode.image.svg.SvgImage)
img.save(TMP_FILE_SVG)

doc = minidom.parse(TMP_FILE_SVG)
rect_tuples = [tuple((convert_xml_attr(path.getAttribute('x')),
                      convert_xml_attr(path.getAttribute("y"))
                      )) for path in doc.getElementsByTagName('rect')]
doc.unlink()
os.remove(TMP_FILE_SVG)

min_max = find_max_min(rect_tuples)
curr_width = find_width(min_max)

width = int(round(MAX_WIDTH / (curr_width))) - 1
start_x = int((MAX_WIDTH - width * (curr_width + 1)) / 2)
start_y = int((MAX_HEIGHT - width * (curr_width + 1)) / 2)

result_list = list()
for it in rect_tuples:
    x = (it[1] - min_max[1]) * width
    y = (it[0] - min_max[0]) * width
    result_list.append(
        tuple((int(x + start_x), int(y + start_y), int(x + start_x + width), int(y + start_y + width))))

result = str()
result_list = sorted(result_list)
for it in result_list:
    result += FORMAT_STRING.format(it[0], it[1], it[2], it[3])

configure_in_file(result, "barcode_bip.c")
