import math
import mido

midi_note_inc = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}

def note_txt_to_midi(note_txt):
    letter = note_txt[0]
    octave = int(note_txt[2])

    if letter == 'R':
        return 0

    if note_txt[1] == '#':
        quality = 1
    elif note_txt[1] == 'B':
        quality = -1
    elif note_txt[1] == 'N':
        quality = 0
    else:
        print(f'Bad note quality: {note}')
        exit(1)

    return ((octave+1)*12) + midi_note_inc[letter] + quality

def duration_txt_to_midi(duration_txt, ticks_per_beat, bpm, tempo):
    seconds = duration_txt*60/bpm
    return int(mido.second2tick(seconds, ticks_per_beat, tempo))

def note_to_midi(note):
    letter = note[0]
    try:
        octave = int(note[2])
        if note[1] == '#':
            quality = 1
        elif note[1] == 'b' or note[1] == 'B':
            quality = -1
        elif note[1] == 'N':
            quality = 0
        else:
            print(f'Error: bad chord component quality: {note[1]}')
            exit(1)
    except IndexError:
        octave = int(note[1])
        quality = 0
    midi = ((octave+1)*12) + midi_note_inc[letter] + quality

    return midi

def sequence_to_midi(sequence):
    return [note_to_midi(note) for note in sequence]

def unzip_sequence(seq):
    notes = [s[0] for s in seq]
    starts = [s[1] for s in seq]
    stops = [s[1] for s in seq]
    return notes, starts, stops

def duration_to_sec(duration, bpm):
    return duration / bpm * 60

def nearest_multiple_above(factor, target):
    return factor*math.ceil(target/factor)
