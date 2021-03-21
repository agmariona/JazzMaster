from datetime import datetime
import fractions
import keyboard
import musthe
import numpy as np
import pychord
import random
import time

import util.constants as c
import util.util as util

HARMONIC_WINDOW=0

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
        print(f'NOTE {pitch} {datetime.now().time()}')
        time.sleep(util.duration_to_sec(duration, bpm))
        keyboard.release(c.note_to_key[note])

def harmonic_reference_test():
    for song in c.reference_songs:
        print(f'{song:>30}:    ', end='')
        harmonic_test(c.PROJ_PATH+f'data/reference_transcriptions/{song}')

def rhythmic_reference_test():
    for song in c.reference_songs:
        print(f'{song:>30}:    ', end='')
        rhythmic_test(c.PROJ_PATH+f'data/reference_transcriptions/{song}')

def gen_rand_chord():
    root = random.choice(roots)
    qual = random.randint(1,2)
    if qual == 1:
        qual = random.choice(major_quals)
    elif qual == 2:
        qual = random.choice(minor_quals)
    else:
        assert False
    return root+qual

def harmonic_random(reffile):
    chords = []
    lf = open(reffile)
    nf = open(reffile)

    for line in lf:
        label, value, time = line.split()
        if label != 'CHORD':
            continue
        time = datetime.strptime(time, '%H:%M:%S.%f')
        chords.append((pychord.Chord(gen_rand_chord()), time))

    chord_groups = [[] for c in chords]
    for line in nf:
        label, value, time = line.split()
        if label != 'NOTE':
            continue
        time = datetime.strptime(time, '%H:%M:%S.%f')

        if time < chords[0][1]:
            continue
        for i in range(len(chords)-1):
            if chords[i][1] <= time < chords[i+1][1]:
                chord_groups[i].append(value[:-1])
                break
        else:
            assert chords[-1][1] <= time
            chord_groups[-1].append(value[:-1])

    bad_notes = 0
    total_notes = 0
    for i in range(len(chords)):
        chord = chords[i][0]
        notes = chord_groups[i]
        quality = chord.quality.quality
        if quality in major_quals:
            quality = 'major'
        elif quality in minor_quals:
            quality = 'natural_minor'
        else:
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

    # print('{:>8}'.format(f'{bad_notes}/{total_notes}\t'), end='')
    # print(f'{bad_notes/total_notes*100:.0f}% error')
    return bad_notes / total_notes

def harmonic_test(logfile, notefile=None):
    chords = []
    lf = open(logfile)
    if notefile:
        nf = open(notefile)
    else:
        nf = open(logfile)

    for line in lf:
        label, value, time = line.split()
        if label != 'CHORD':
            continue
        time = datetime.strptime(time, '%H:%M:%S.%f')
        chords.append((pychord.Chord(value), time))

    chord_groups = [[] for c in chords]
    for line in nf:
        label, value, time = line.split()
        if label != 'NOTE':
            continue
        time = datetime.strptime(time, '%H:%M:%S.%f')

        if time < chords[0][1]:
            continue
        for i in range(len(chords)-1):
            if chords[i][1] <= time < chords[i+1][1]:
                chord_groups[i].append(value[:-1])
                break
        else:
            assert chords[-1][1] <= time
            chord_groups[-1].append(value[:-1])

    bad_notes = 0
    total_notes = 0
    for i in range(len(chords)):
        chord = chords[i][0]
        notes = chord_groups[i]
        quality = chord.quality.quality
        if quality in major_quals:
            quality = 'major'
        elif quality in minor_quals:
            quality = 'natural_minor'
        else:
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

    # print('{:>8}'.format(f'{bad_notes}/{total_notes}\t'), end='')
    # print(f'{bad_notes/total_notes*100:.0f}% error')
    return bad_notes / total_notes

def rhythmic_test(logfile):
    times = []
    start_time = 0
    with open(logfile) as f:
        bpm = 120 # GENERALIZE
        ibi = 60 / bpm

        label, _, time = f.readline().split()
        start_time = time
        if label == 'CHORD':
            times.append(datetime.strptime(time, "%H:%M:%S.%f"))

        for line in f:
            label, _, time = line.split()
            if label == 'CHORD':
                times.append(datetime.strptime(time, "%H:%M:%S.%f"))
    times = np.array([(time - times[0]).total_seconds() for time in times])

    mistimed_chords = 0
    total_chords = len(times)
    for time in times:
        nearest = util.nearest_multiple(ibi/2, time)
        if abs(time - nearest) > c.RHYTHM_TEST_WINDOW:
            mistimed_chords += 1
    # print('{:>8}'.format(f'{mistimed_chords}/{total_chords}\t'), end='')
    # print(f'{mistimed_chords/total_chords*100:.0f}% error')
    return mistimed_chords/total_chords

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
            n_mismatch += 1
    print(
        f'{n_iter} pairs, {n_mismatch} mismatches, {n_mismatch/n_iter}% error')

roots = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
major_quals = ['', 'maj', '6', 'maj9', 'maj7']
minor_quals = ['m', 'm7', 'm6', 'm9', 'm7b5']
