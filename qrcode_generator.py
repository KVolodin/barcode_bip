import barcode
import logging
import qrcode
import qrcode.image.svg
from collections import namedtuple
from argparse import ArgumentParser
from pdf417 import encode, render_svg
from xml.dom import minidom

Barcode = namedtuple('Barcode', 'code type name')
MinMax = namedtuple('MinMax', 'min_x min_y max_x max_y')
Point = namedtuple('Point', 'x y')
PointWidth = namedtuple('PointWidth', 'x width')
Rect = namedtuple('Rect', 'x y width height')

BARCODE_FOLDER = 'barcode'
FORMAT_FILLED_RECT_VERT_STRING = '\t\t\tdraw_filled_rect({:.0f}, 45, {:.0f}, 160);\n'
FORMAT_VERTICAL_LINE_STRING = '\t\t\tdraw_vertical_line({:.0f}, 45, 160);\n'
FORMAT_FILLED_RECT_STRING = "\t\t\tdraw_filled_rect({:.0f}, {:.0f}, {:.0f}, {:.0f});\n"
FILE_NAME = "barcode_bip.c"

MAX_WIDTH = 175
MAX_HEIGHT = 175

logging.basicConfig(format=u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_xml_attr(attr):
    return float(str(attr).replace("mm", ""))


def get_parser():
    """ create arguments parser """
    arg_parser = ArgumentParser(
        __name__, prefix_chars='--', description='Generates barcode')

    arg_parser.add_argument('-t', "--text",
                            nargs='+',
                            help='enter you barcode example 555555555:upc:Ashan',
                            required=True)

    return arg_parser


def configure_in_file(replace_string, replace_count_screen, fileName):
    with open(fileName + ".in", 'r') as file:
        result = file.read()

    result = result.replace("@REPLACE_COUNT_SCREEN@", replace_count_screen)
    result = result.replace("@REPLACE_STRING@", replace_string)

    with open(fileName, 'w') as file:
        file.write(result)


def configure_switch(string, screen_num):
    return "\t\tcase SCREEN_" + str(screen_num) + ":\n" + string + "\t\t\tbreak;\n"


def find_max_min(points):
    min_x = MAX_WIDTH
    min_y = MAX_HEIGHT
    max_x = 0
    max_y = 0
    for it in points:
        if min_x > it.x:
            min_x = it.x
        if it.x > max_x:
            max_x = it.x
        if min_y > it.y:
            min_y = it.y
        if it.y > max_y:
            max_y = it.y
    return MinMax(min_x, min_y, max_x, max_y)


def find_width(min_max):
    width_height = tuple((min_max[2] - min_max[0], min_max[3] - min_max[1]))
    if width_height[0] != width_height[1]:
        logger.error("it's not a square")
        return -1
    if width_height[0] > MAX_WIDTH:
        logger.error("Current width:" + str(width_height[0]) +
                     " more than " + str(MAX_WIDTH))
        return -1
    return width_height[0]


def generate_barcode(name):
    doc = minidom.parse(name + '.svg')
    rect_tuples = [Rect(convert_xml_attr(path.getAttribute('x')),
                        convert_xml_attr(path.getAttribute("y")),
                        convert_xml_attr(path.getAttribute("width")),
                        convert_xml_attr(path.getAttribute("height"))
                        ) for path in doc.getElementsByTagName('rect')
                   if not path.getAttribute('style') != 'fill:black;']
    doc.unlink()

    min_x = MAX_WIDTH
    for it in rect_tuples:
        if min_x > it.x:
            min_x = it.x

    min_width = float(MAX_WIDTH)
    for it in rect_tuples:
        if min_width > it.width:
            min_width = it.width

    rect_tuples = [PointWidth(round((rect.x - min_x) / min_width),
                              round(rect.width / min_width)
                              ) for rect in rect_tuples]

    max_x = 0
    for it in rect_tuples:
        if it.x > max_x:
            max_x = it.x
    start_x = int((MAX_WIDTH - max_x) // 2)

    result = str()
    for it in rect_tuples:
        if it.width > 1:
            result += FORMAT_FILLED_RECT_VERT_STRING.format(
                it.x + start_x, it.x + start_x + it.width - 1)
        else:
            result += FORMAT_VERTICAL_LINE_STRING.format(it.x + start_x)

    result += "\t\t\ttext_out_center(\"" + name + "\", 88, 11);\n"
    return result


def generate_qrcode(name):
    doc = minidom.parse(name + '.svg')
    rect_tuples = [Point(convert_xml_attr(path.getAttribute('x')),
                         convert_xml_attr(path.getAttribute("y"))
                         ) for path in doc.getElementsByTagName('rect')]
    doc.unlink()

    min_max = find_max_min(rect_tuples)
    curr_width = find_width(min_max)
    if curr_width < 0:
        return ""

    width = int(round(MAX_WIDTH / curr_width)) - 1
    start_x = int((MAX_WIDTH - width * (curr_width + 1)) / 2)
    start_y = int((MAX_HEIGHT - width * (curr_width + 1)) / 2)

    result_list = list()
    for it in rect_tuples:
        x = (it.y - min_max[1]) * width
        y = (it.x - min_max[0]) * width
        result_list.append(
            Rect(int(x + start_x), int(y + start_y), int(x + start_x + width), int(y + start_y + width)))

    result = str()
    for it in result_list:
        result += FORMAT_FILLED_RECT_STRING.format(
            it.x, it.y, it.width, it.height)
    return result


def generate_417_barcode(name):
    doc = minidom.parse(name + '.svg')
    rects = [Rect(int(path.getAttribute('x')),
                  int(path.getAttribute("y")),
                  int(path.getAttribute("width")),
                  int(path.getAttribute("height"))) for path in doc.getElementsByTagName('rect')]
    doc.unlink()

    width = rects[0].width
    for rc in rects:
        if rc.width != width:
            return ""

    minMax = find_max_min(rects)
    start_x = (MAX_WIDTH - ((minMax.max_x / width) - (minMax.min_x/width))) // 2
    start_y = (MAX_WIDTH - (minMax.max_y - minMax.min_y)) // 2

    result = str()
    for it in rects:
        result += FORMAT_FILLED_RECT_STRING.format(
            (it.x / width) + start_x,
            it.y + start_y,
            (it.x / width) + start_x,
            it.y + it.height + start_y)

    result += "\t\t\ttext_out_center(\"" + name + "\", 88, 11);\n"
    return result


def main():
    """ Main """
    args = get_parser().parse_args()

    logger.info(args)

    barcodes = [str(text).split('::') for text in args.text]

    for bar in barcodes:
        if len(bar) != 3:
            logger.error("Invalid Argument")
            exit(1)

    barcodes_svg = list()
    barcodes_417_svg = list()
    barcodes_qrcode_svg = list()
    for bar in barcodes:
        bar_name = Barcode(bar[0], bar[1], bar[2])
        if bar[1] == 'pdf417':
            barcodes_417_svg.append(bar_name)
        elif bar[1] == 'qrcode':
            barcodes_qrcode_svg.append(bar_name)
        else:
            barcodes_svg.append(bar_name)

    for bar in barcodes_svg:
        barcode.get(bar.type, bar.code).save(bar.name)
        print("output file: " + str(bar))

    for bar in barcodes_417_svg:
        render_svg(encode(bar.code)).write(bar.name + '.svg')
        print("output file: " + str(bar))

    for bar in barcodes_qrcode_svg:
        qrcode.make(bar.code, image_factory=qrcode.image.svg.SvgImage).save(
            bar.name + '.svg')
        print("output file: " + str(bar))

    result = str()
    count_screen_str = str()

    count_screen = len(barcodes_svg) + \
        len(barcodes_417_svg) + len(barcodes_qrcode_svg)
    for i in range(count_screen):
        count_screen_str += "\tSCREEN_" + str(i) + ",\n"

    current_screen = 0
    for bar in barcodes_svg:
        result += configure_switch(generate_barcode(bar.name), current_screen)
        current_screen = current_screen + 1

    for bar in barcodes_417_svg:
        result += configure_switch(generate_417_barcode(bar.name),
                                   current_screen)
        current_screen = current_screen + 1

    for bar in barcodes_qrcode_svg:
        result += configure_switch(generate_qrcode(bar.name), current_screen)
        current_screen = current_screen + 1

    configure_in_file(result, count_screen_str, FILE_NAME)


if __name__ == "__main__":
    main()
