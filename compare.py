import pandas as pd

import util.util as util

db = pd.read_pickle('resources/compare.db')

def get_matches(seq):
    ngram = midi_to_ngram(seq)
    print(ngram)
    matches = db[db.ngram==ngram]
    if matches.empty:
        print('Error: Match not found. Only exact matching supported.')
        return None

    # Information comes from *next* ngram
    to_drop = []
    for i, r in matches.iterrows():
        if db.iloc[i].track != db.iloc[i+1].track:
            to_drop.append(i)
    matches = matches.drop(to_drop)
    matches = db.iloc[matches.index+1]

    if matches.empty:
        print('Error: End of song.')
        return None

    return matches

def sequence_to_ngram(seq):
    midi_seq = util.sequence_to_midi(sequence)
    return midi_to_ngram(midi_seq)

def midi_to_ngram(midi_seq):
    midi_seq[1:] = [midi_seq[i]-midi_seq[i-1]
        for i in range (1, len(midi_seq))]
    midi_seq[0] = 0
    ngram = ' '.join(map(str, midi_seq))
    return ngram
