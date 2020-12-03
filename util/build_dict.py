import pandas as pd

from util import note_txt_to_midi, duration_txt_to_midi

TRACKS = [
    'take_the_a_train',
    'satin_doll',
    'misty'
]
NGRAM_SIZE = 5
COLUMNS = ['ngram', 'harmony', 'duration', 'initial', 'track', 'position']

db = pd.DataFrame(columns=COLUMNS)

for track in TRACKS:
    txt = open(f'../library/{track}.txt')
    bpm, time_sig = txt.readline().split('/')

    notes = list()
    chords = list()
    durations = list()
    for line in txt:
        note, duration, chord = line.split()
        if note[0] == 'R':
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

        entry = pd.DataFrame([[ngram, harmony, duration, initial, track, i]],
            columns=COLUMNS)
        db = db.append(entry, ignore_index=True)

print(db.head())
print(db.tail())
db.to_pickle('../resources/compare.db')
