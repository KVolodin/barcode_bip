# https://topresale.ru/generator-shtrih-koda-onlayn/
from xml.dom import minidom
from math import ceil
from argparse import ArgumentParser
import logging
import sys, os

MAX_WIDTH = 175
MAX_HEIGHT = 175

parser = ArgumentParser()
parser.add_argument("-p", "--path", dest="path",
                    help="svg file path", metavar="FILE")
args = parser.parse_args()

if not (args.path):
	logging.error("No parameter specified")
	print(parser.print_help())
	sys.exit(1)

filename = os.path.splitext(args.path)
head_tail = os.path.split(filename[0])
if (filename[1] != ".svg"):
    logging.error(filename[1] + " is not svg file")
    print(parser.print_help())
    sys.exit(1)

dom = minidom.parse(args.path)  # parseString also exists
dom.normalize()

min_x = -1
max_x = 0

for child in dom.getElementsByTagName("rect"):
    color = child.getAttribute("fill")
    if(color == "white" or color == "#ffffff"):
        continue
    color = child.getAttribute("style")
    if(color == "fill:white" or color == "fill:#ffffff;"):
        continue
    x = int(child.getAttribute("x"))
    if(min_x == -1):
        min_x = x
    width = int(child.getAttribute("width"))
    x = x + width
    if(x > max_x):
        max_x = x
start = ceil((MAX_WIDTH - max_x - min_x)/2)

if(max_x + start > MAX_WIDTH):
    logging.error("Current width:" + str(max_x + start) +
                  " more than " + str(MAX_WIDTH))
    sys.exit(1)

# for transform in dom.getElementsByTagName("g"):
#     string = (transform.getAttribute("transform").split("(")[1].split(","))
#     trans = int(string[0])

y_start = "45"
y_end = "160"
result = str()
for child in dom.getElementsByTagName("rect"):
    color = child.getAttribute("fill")
    if(color == "white" or color == "#ffffff"):
        continue
    color = child.getAttribute("style")
    if(color == "fill:white" or color == "fill:#ffffff;"):
        continue
    x = ceil(int(child.getAttribute("x")) * 1)
    width = ceil(int(child.getAttribute("width")) * 1)

    if(width > 1):
        result += "\t\t\tdraw_filled_rect(" + str(x + start) + ", " + y_start + ", " + str(
            x + start + width - 1) + ", " + y_end + ");\n"
    else:
        result += "\t\t\tdraw_vertical_line(" + str(
            x + start) + ", " + y_start + ", " + y_end + ");\n"

dom.unlink()

result += "\t\t\tdraw_rect(40, 5, 134, 33);\n"
result += "\t\t\ttext_out_center(\"" + head_tail[1] + "\", 88, 11);\n"

filedata = str()
with open("barcode_bip.c.in", 'r') as file:
    filedata = file.read()

filedata = filedata.replace("@REPLACE_STRING@", result)

with open("barcode_bip.c", 'w') as file:
    file.write(filedata)
