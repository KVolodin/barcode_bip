# https://topresale.ru/generator-shtrih-koda-onlayn/

from xml.dom import minidom
from math import ceil
from argparse import ArgumentParser
import logging
import sys
import os

from itertools import tee, islice, chain


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

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
if (filename[1] != ".svg"):
    logging.error(filename[1] + " is not svg file")
    print(parser.print_help())
    sys.exit(1)

dom = minidom.parse(args.path)
dom.normalize()

min_x = -1
max_x = 0

min_y = -1
max_y = 0

for child in dom.getElementsByTagName("rect"):
    color = child.getAttribute("fill")
    if(color == "white" or color == "#ffffff"):
        continue
    color = child.getAttribute("style")
    if(color == "fill:white" or color == "fill:#ffffff;"):
        continue
    x = int(child.getAttribute("x"))
    y = int(child.getAttribute("y"))

    if(min_x == -1):
        min_x = x

    if(x > max_x):
        max_x = x

    if(min_y == -1):
        min_y = y

    if(y > max_y):
        max_y = y

dist = max_x - min_x
if (dist != max_y - min_y):
    logging.error("Invalide svg file")
    sys.exit(1)

width = int(round(MAX_WIDTH / (dist))) - 1
start_x = int((MAX_WIDTH - width * dist) / 2)
start_y = int((MAX_HEIGHT - width * dist) / 2)

if(max_x + start_x > MAX_WIDTH):
    logging.error("Current width:" + str(max_x + start_x) +
                  " more than " + MAX_WIDTH)
    sys.exit(1)

if(max_y + start_y > MAX_HEIGHT):
    logging.error("Current height:" + str(max_x) + " more than " + MAX_HEIGHT)
    sys.exit(1)

a_list = list()
result = ""
for child in dom.getElementsByTagName("rect"):
    color = child.getAttribute("fill")
    if(color == "white" or color == "#ffffff"):
        continue
    color = child.getAttribute("style")
    if(color == "fill:white" or color == "fill:#ffffff;"):
        continue
    x = int(child.getAttribute("x"))
    y = int(child.getAttribute("y"))

    x = (int(child.getAttribute("y")) - min_y) * width
    y = (int(child.getAttribute("x")) - min_x) * width
    a_list.append(tuple((
        x + start_x,
        y + start_y,
        x + start_x + width,
        y + start_y + width)))

dom.unlink()

a_list = sorted(a_list)
unique_list = list()
for previous, item, nxt in previous_and_next(a_list):
    if(nxt == None or (nxt[0] != item[0] or nxt[2] != item[2])):
        unique_list.append(item)

result_list = list()
for it in unique_list:
    new_list = list(
        filter(lambda x: x[0] == it[0] and x[2] == it[2], a_list))
    if not new_list:
        continue
    from_y = new_list[0][1]
    for previous, item, nxt in previous_and_next(new_list):
        if(nxt == None or (nxt[2] - item[2] != width and nxt[3] - item[3] != width)):
            result_list.append(tuple((item[0], from_y, item[2], item[3])))
            if(nxt != None):
                from_y = nxt[1]

for it in result_list:
    result += "\t\t\tdraw_filled_rect(" + str(it[0]) + ", " + \
        str(it[1]) + ", " + str(it[2]) + ", " + str(it[3]) + ");\n"

filedata = str()
with open("barcode_bip.c.in", 'r') as file:
    filedata = file.read()

filedata = filedata.replace("@REPLACE_STRING@", result)

with open("barcode_bip.c", 'w') as file:
    file.write(filedata)
