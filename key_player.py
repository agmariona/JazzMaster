import argparse
from datetime import datetime
import fractions
import keyboard
import mido
import pychord
import threading
import time

import util.constants as c
import util.util as util
from core import play

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('txt', type=str, help='path to .txt to convert')
parser.add_argument('-b', type=int, default=120, help='tempo')
parser.add_argument('-c', action='store_true', help='play chords')
parser.add_argument('-s', action='store_false', help='silent mode')
parser.add_argument('-n', action='store_false', help='don\'t press keys')
parser.add_argument('-w', action='store_true', help='write test logs')
args = parser.parse_args()

bpm = args.b

if args.w:
    for song in c.reference_songs:
        infile = open(c.PROJ_PATH+f'library/txt/{song}', 'r')
        outfile = open(
            c.PROJ_PATH+f'data/reference_transcriptions/{song}', 'w+')

        current_chord = None
        for line in infile:
            note, duration, chord = line.split()
            duration = float(fractions.Fraction(duration))
            if chord != 'None' and chord != current_chord:
                outfile.write(f'CHORD {chord} {datetime.now().time()}\n')
                current_chord = chord
            if note[0] == 'R':
                time.sleep(util.duration_to_sec(duration, bpm))
            else:
                outfile.write(
                    f'NOTE {util.canonical_note(note)} ' + \
                    f'{datetime.now().time()}\n')
                time.sleep(util.duration_to_sec(duration, bpm))
    exit()

txt = open(args.txt)
time.sleep(1)

current_chord = None
for line in txt:
    note, duration, chord = line.split()
    duration = float(fractions.Fraction(duration))

    if args.c and chord != 'None' and chord != current_chord:
        print(f'CHORD {chord} {datetime.now().time()}')
        current_chord = chord
        if args.s:
            threading.Thread(target=play.play_chord_async,
                args=(pychord.Chord(current_chord), 3)).start()

    if note[0] == 'R':
        time.sleep(util.duration_to_sec(duration, bpm))
    else:
        print(f'NOTE {util.canonical_note(note)} {datetime.now().time()}')
        if args.n:
            keyboard.press(c.note_to_key[note])
        time.sleep(util.duration_to_sec(duration, bpm))
        if args.n:
            keyboard.release(c.note_to_key[note])

with mido.open_output() as outport:
    outport.send(mido.Message('stop'))
