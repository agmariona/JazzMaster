import argparse
import os

import constants
import xml_parser

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-x', default=None, type=str,
    help='path to .xml to parse')
parser.add_argument('-m', default=0, type=int,
    help='maximum number of songs to translate')
args = parser.parse_args()

if args.x:
    assert args.x.split('/')[-1].split('.')[-1] == 'xml'
    xml_parser.parse_xml(args.x)
else:
    dirpath = constants.PROJ_PATH + 'library/jazz_scores'
    count = 0
    for f in os.listdir(os.fsencode(dirpath)):
        filename = os.fsdecode(f)
        path = os.path.join(dirpath, filename)
        xml_parser.parse_xml(path)

        count += 1
        if args.m and count == args.m:
            exit()
