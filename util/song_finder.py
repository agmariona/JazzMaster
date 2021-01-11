import argparse
import os
import string
import subprocess
import unidecode

import constants

def remove_punct(s):
    return s.translate(str.maketrans('', '', string.punctuation))

def as_single_quotes(s):
    return s.translate(str.maketrans(
                {"'": "\\'", '"': "\\'", '“': "\\'", '”': "\\'"}))

def as_double_quotes(s):
    return s.translate(str.maketrans(
                {"'": '\\"', '"': '\\"', '“': '\\"', '”': '\\"'}))

def as_proper_name(s):
    s = s.lower().strip()
    s = remove_punct(s)
    s = s.translate(str.maketrans(' ', '_'))
    return(s)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-w', action='store_true', help='rebuild search list')
parser.add_argument('-m', type=int, default=0,
    help='max number of songs to check')
args = parser.parse_args()

list_path = constants.PROJ_PATH + 'library/search_songs.txt'
find_path = constants.PROJ_PATH + 'library/scores'
find_path = find_path.translate(str.maketrans({' ': '\ '}))
target_path = find_path.replace('scores', 'jazz_scores')

if args.w:
    in_path = constants.PROJ_PATH + 'library/songs.txt'
    with open(in_path) as infile, open(list_path, 'w') as outfile:
        print('Rewriting search list.')
        for inline in infile:
            no_parens = inline.split('(')[0].strip()
            if not no_parens:
                no_parens = inline.split(')')[-1].strip()
            no_parens = unidecode.unidecode(no_parens)
            single_quotes = as_single_quotes(no_parens)
            double_quotes = as_double_quotes(no_parens)
            no_punct = remove_punct(no_parens)
            if single_quotes != no_parens:
                outfile.write(single_quotes+'\n')
                if double_quotes != single_quotes:
                    outfile.write(double_quotes+'\n')
            else:
                outfile.write(no_parens+'\n')
            if no_punct != no_parens:
                outfile.write(no_punct+'\n')

print(f'Emptying current library at {target_path}.')
cmd = f'rm -f {target_path}/*'
ret = subprocess.run(cmd, shell=True)

with open(list_path) as infile:
    print('Searching for songs.')
    count = 0
    song_counters = dict()
    for line in infile:
        proper_name = as_proper_name(line)
        try:
            dup_count = song_counters[proper_name]
        except KeyError:
            song_counters[proper_name] = 0

        cmd = f'find {find_path} -iname "* - {line.strip()}.xml"'
        ret = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        results = ret.stdout.split('\n')
        results = [result for result in results if result]

        for result in results:
            assigned_name = proper_name + f'_{song_counters[proper_name]}'
            song_counters[proper_name] += 1

            name = os.path.basename(result).split('.')[0]
            target = result.replace('scores', 'jazz_scores')
            target = target.replace(name, assigned_name)

            cmd = f'cp "{result}" "{target}"'
            subprocess.run(cmd, shell=True)
            count += 1
        if args.m and count > args.m:
            exit()

    songs_found = {k: v for k, v in song_counters.items() if v > 0}
    print(f'Found {count} files and {len(songs_found)} distinct songs.')
