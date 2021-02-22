import pandas as pd
import os

import constants as c
from util import note_txt_to_midi, duration_txt_to_midi

NGRAM_SIZE = 5
COLUMNS = ['ngram', 'harmony', 'duration', 'initial', 'track', 'position']

db = pd.DataFrame(columns=COLUMNS)

for filename in os.listdir(c.PROJ_PATH + 'library/txt/'):
    print(filename)
    txt = open(c.PROJ_PATH+'library/txt/'+filename)

    notes = list()
    chords = list()
    durations = list()

    for line in txt:
        note, duration, chord = line.split()
        if note[0] == 'R':
            continue
        if note == 'None':
            continue
        notes.append(note_txt_to_midi(note))
        chords.append(chord)
        durations.append(duration)

    for i in range(len(notes) - NGRAM_SIZE + 1):
        ngram = notes[i:i+NGRAM_SIZE]
        harmony = chords[i:i+NGRAM_SIZE]
        duration = durations[i:i+NGRAM_SIZE]
        initial = ngram[0]

        ngram[1:] = [ngram[i]-ngram[i-1] for i in range (1, len(ngram))]
        ngram[0] = 0

        ngram = ' '.join(map(str, ngram))
        harmony = ' '.join(map(str, harmony))
        duration = ' '.join(map(str, duration))

        entry = pd.DataFrame([[ngram, harmony, duration, initial, filename, i]],
            columns=COLUMNS)
        db = db.append(entry, ignore_index=True)

    txt.close()

db.to_pickle('../resources/compare.db')
