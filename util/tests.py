from datetime import datetime
import fractions
import keyboard
import musthe
import pychord
import time

import util.constants as c
import util.util as util

HARMONIC_WINDOW=1

def listen_test(sweep, bpm):
    time.sleep(1)
    for line in sweep:
        note, duration = line.split()
        duration = float(fractions.Fraction(duration))

        keyboard.press(c.note_to_key[note])
        if note[1] == 'N':
            pitch = note[0]+note[2]
        else:
            pitch = note
        print(f'{pitch} {datetime.now().time()}')
        time.sleep(util.duration_to_sec(duration, bpm))
        keyboard.release(c.note_to_key[note])

def harmonic_reference_test():
    for song in c.reference_songs:
        print(f'{song:>30}:    ', end='')
        harmonic_test(c.PROJ_PATH+f'data/reference_transcriptions/{song}')

def harmonic_test(logfile):
    chord_groups = []
    with open(logfile) as f:
        for line in f:
            label, value, _ = line.split()
            if label == 'CHORD':
                chord_groups.append((pychord.Chord(value), []))
            elif label == 'NOTE' and len(chord_groups) > 0:
                chord_groups[-1][1].append(value[:-1])

    bad_notes = 0
    total_notes = 0
    for group in chord_groups:
        chord = group[0]
        notes = group[1]
        quality = chord.quality.quality
        if quality in major_quals:
            quality = 'major'
        elif quality in minor_quals:
            quality = 'natural_minor'
        else:
            print(f'\nMissing scale for chord {chord}')
            quality = None

        if quality:
            scale = musthe.Scale(musthe.Note(chord.root), quality)
            scale_notes = [str(scale[i]) for i in range(len(scale))]
        else:
            scale = []

        for i in range(len(notes)):
            lower = max(0, i-HARMONIC_WINDOW)
            upper = min(len(notes)-1, i+HARMONIC_WINDOW)
            relevant_notes = [notes[j] for j in range(lower, upper+1)]

            for note in relevant_notes:
                if note in chord.components() or musthe.Note(note) in scale:
                    break
            else:
                bad_notes += 1

        total_notes += len(notes)

    print('{:>8}'.format(f'{bad_notes}/{total_notes}\t'), end='')
    print(f'{bad_notes/total_notes:.2f}%')

def note_test(file_a, file_b):
    notes_a = []
    notes_b = []
    with open(file_a) as f:
        for line in f:
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

major_quals = ['', 'maj', '7', 'sus4', '9', '6', '13', 'maj9', '11', '69',
    'maj7', '7sus4', '5', '7#5', 'mM7', 'aug']
minor_quals = ['m', 'm7', 'm6', 'm9', 'm7b5', 'dim', 'dim6']
