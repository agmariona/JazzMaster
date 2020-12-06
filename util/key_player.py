import argparse
import fractions
import keyboard
import time

import util as util

note_to_key = {
    'GN3': 'w',
    'G#3': '3',
    'AB3': '3',
    'AN3': 'e',
    'A#3': '4',
    'BB3': '4',
    'BN3': 'r',
    'CN4': 't',
    'C#4': '6',
    'DB4': '6',
    'DN4': 'y',
    'D#4': '7',
    'EB4': '7',
    'EN4': 'u',
    'FN4': 'i',
    'F#4': '9',
    'GB4': '9',
    'GN4': 'o',
    'G#4': '0',
    'AB4': '0',
    'AN4': 'p',
    'A#4': '-',
    'BB4': '-',
    'BN4': '[',
    'CN5': 'z',
    'C#5': 's',
    'DB5': 's',
    'DN5': 'x',
    'D#5': 'd',
    'EB5': 'd',
    'EN5': 'c',
    'FB5': 'c',
    'FN5': 'v',
    'F#5': 'g',
    'GB5': 'g',
    'GN5': 'b',
    'G#5': 'h',
    'AB5': 'h',
    'AN5': 'n',
    'A#5': 'j',
    'BB5': 'j',
    'BN5': 'm',
}

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('txt', type=str, help='path to .txt to convert')
args = parser.parse_args()

txt = open(args.txt)
bpm, time_sig = txt.readline().split('/')
bpm = float(bpm)

time.sleep(5)

for line in txt:
    note, duration, chord = line.split()
    duration = float(fractions.Fraction(duration))
    if note[0] == 'R':
        time.sleep(util.duration_to_sec(duration, bpm))
    else:
        keyboard.press(note_to_key[note])
        time.sleep(util.duration_to_sec(duration, bpm))
        keyboard.release(note_to_key[note])
