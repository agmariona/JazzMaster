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
    err_count = 0
    for f in os.listdir(os.fsencode(dirpath)):
        filename = os.fsdecode(f)
        path = os.path.join(dirpath, filename)
        r = xml_parser.parse_xml(path)
        if r == -1:
            print(f'\tError translating {filename}: excess parts.')
            err_count += 1
        elif r == -2:
            print(f'\tError translating {filename}: endings.')
            err_count += 1
        elif r == -3:
            print(f'\tError translating {filename}: pitch formatting.')
            err_count += 1
        elif r == -4:
            print(f'\tError translating {filename}: polyphonic.')
            err_count += 1
        else:
            count += 1

        if args.m and count == args.m:
            exit()
    print(f'Translated {count} songs. Failed to translate {err_count} songs.')
