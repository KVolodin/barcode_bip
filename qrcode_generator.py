import qrcode
import qrcode.image.svg
from argparse import ArgumentParser
import logging
import sys

from xml.dom import minidom

# Constants
SVG_FILE = "qrcode.svg"
FORMAT_STRING = "\t\t\tdraw_filled_rect({:.0f}, {:.0f}, {:.0f}, {:.0f});\n"
MAX_WIDTH = 175
MAX_HEIGHT = 175


def get_parser():
    """ create arguments parser """
    arg_parser = ArgumentParser(
        __name__, prefix_chars='--', description='Generates barcode')

    arg_parser.add_argument("-t", "--text",
                            required=True,
                            dest="text",
                            type=str,
                            help="enter you text", )

    arg_parser.add_argument("-s", "--svg",
                            dest="svg",
                            type=str,
                            nargs= '?',
                            help="output svg file",
                            default=SVG_FILE)

    return arg_parser


def convert_xml_attr(attr):
    return int(str(attr).replace("mm", ""))


def configure_in_file(result, fileName):
    with open(fileName + ".in", 'r') as file:
        result = file.read()

    result = result.replace("@REPLACE_STRING@", result)

    with open(fileName, 'w') as file:
        file.write(result)


def find_max_min(rect_tuples):
    min_x = MAX_WIDTH
    min_y = MAX_HEIGHT
    max_x = 0
    max_y = 0
    for it in rect_tuples:
        x = it[0]
        y = it[1]
        if min_x > x:
            min_x = x
        if x > max_x:
            max_x = x
        if min_y > y:
            min_y = y
        if y > max_y:
            max_y = y
    return tuple((min_x, min_y, max_x, max_y))


def find_width(min_max, logger):
    width_height = tuple((min_max[2] - min_max[0], min_max[3] - min_max[1]))
    if width_height[0] != width_height[1]:
        logger.error("it's not a square")
        sys.exit(1)
    if width_height[0] > MAX_WIDTH:
        logger.error("Current width:" + str(width_height[0]) +
                      " more than " + str(MAX_WIDTH))
        sys.exit(1)
    return width_height[0]


def main():
    """ Main """
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    args = get_parser().parse_args()

    logger.info(args)

    img = qrcode.make(args.text, image_factory=qrcode.image.svg.SvgImage)
    img.save(args.svg)
    logger.info("output file: " + args.svg)
    #print("output file: " + args.svg)

    doc = minidom.parse(args.svg)
    rect_tuples = [tuple((convert_xml_attr(path.getAttribute('x')),
                          convert_xml_attr(path.getAttribute("y"))
                          )) for path in doc.getElementsByTagName('rect')]
    doc.unlink()

    min_max = find_max_min(rect_tuples)
    curr_width = find_width(min_max, logger)

    width = int(round(MAX_WIDTH / curr_width)) - 1
    start_x = int((MAX_WIDTH - width * (curr_width + 1)) / 2)
    start_y = int((MAX_HEIGHT - width * (curr_width + 1)) / 2)

    result_list = list()
    for it in rect_tuples:
        x = (it[1] - min_max[1]) * width
        y = (it[0] - min_max[0]) * width
        result_list.append(
            tuple((int(x + start_x), int(y + start_y), int(x + start_x + width), int(y + start_y + width))))

    result = str()
    for it in result_list:
        result += FORMAT_STRING.format(it[0], it[1], it[2], it[3])

    configure_in_file(result, "barcode_bip.c")

    logger.info("Success generate barcode_bip.c, run build.bat")


if __name__ == "__main__":
    main()
