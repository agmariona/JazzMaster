import argparse
import os
import string
import subprocess

import constants

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-w', action='store_true', help='rebuild search list')
args = parser.parse_args()

list_path = constants.PROJ_PATH + 'library/search_songs.txt'
find_path = constants.PROJ_PATH + 'library/scores'
find_path = find_path.translate(str.maketrans({' ': '\ '}))

if args.w:
    in_path = constants.PROJ_PATH + 'library/songs.txt'
    with open(in_path) as infile, open(list_path, 'w') as outfile:
        for inline in infile:
            no_parens = inline.split('(')[0].strip()
            no_parens = \
                no_parens.translate(str.maketrans(
                    {"'": "\\'", '"': '\\"', '“': '\\"', '”': '\\"'}))
            no_punct = \
                no_parens.translate(str.maketrans('', '', string.punctuation))
            outfile.write(no_parens+'\n')
            if no_punct != no_parens:
                outfile.write(no_punct+'\n')

with open(list_path) as infile:
    count = 0
    for line in infile:
        ret = subprocess.run(
            f'find {find_path} -iname "* - *{line.strip()}.xml"',
            shell=True, capture_output=True, text=True)
        if ret.stdout:
            # print(os.path.basename(ret.stdout).strip())
            count += 1
    print(count)
