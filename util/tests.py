from datetime import datetime
import fractions
import keyboard
import time

import util.util as util

def listen_test(sweep, bpm):
    time.sleep(1)
    for line in sweep:
        note, duration = line.split()
        duration = float(fractions.Fraction(duration))

        keyboard.press(note_to_key[note])
        if note[1] == 'N':
            pitch = note[0]+note[2]
        else:
            pitch = note
        print(f'{pitch} {datetime.now().time()}')
        time.sleep(util.duration_to_sec(duration, bpm))
        keyboard.release(note_to_key[note])

def note_test(file_a, file_b):
    notes_a = []
    notes_b = []
    with open(file_a) as f:
        for line in f:
            print(line)
            label, note, _ = line.split()
            if label == 'NOTE':
                notes_a.append(note)
    with open(file_b) as f:
        for line in f:
            label, note, _ = line.split()
            if label == 'NOTE':
                notes_b.append(note)

    n_iter = max(len(notes_a), len(notes_b))
    n_mismatch = 0
    for i in range(n_iter):
        try:
            a = notes_a[i]
        except IndexError:
            a = ''
        try:
            b = notes_b[i]
        except IndexError:
            b = ''

        if a != b:
            print(f'MISMATCH @ {i}: {a} {b}')
            n_mismatch += 1
    print(
        f'{n_iter} pairs, {n_mismatch} mismatches, {n_mismatch/n_iter}% error')

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
    'CB5': '[',
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
    'CN6': ',',
    'C#6': 'l',
    'DN6': '.',
    'D#6': ';',
    'EN6': '/'
}

