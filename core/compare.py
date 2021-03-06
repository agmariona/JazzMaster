import pandas as pd
import fuzzyset
import sys

import util.util as util
import util.constants as c

db = pd.read_pickle(f'resources/compare_{c.N_NGRAM}.db')
match_set = fuzzyset.FuzzySet(db.ngram)

def get_matches(seq):
    ngram = midi_to_ngram(seq)
    best_match = match_set.get(ngram)[0][1]
    matches = db[db.ngram==best_match]

    # Information comes from *next* ngram
    to_drop = []
    for i, r in matches.iterrows():
        if i+c.N_NGRAM >= len(db):
            to_drop.append(i)
        elif db.iloc[i].track != db.iloc[i+c.N_NGRAM].track:
            to_drop.append(i)
        elif db.iloc[i].track in c.reference_songs:
            to_drop.append(i)
    matches = matches.drop(to_drop)
    next_matches = db.iloc[matches.index+c.N_NGRAM]

    if matches.empty:
        # print('Error: End of song.')
        return None, None

    return matches, next_matches

def sequence_to_ngram(seq):
    midi_seq = util.sequence_to_midi(sequence)
    return midi_to_ngram(midi_seq)

def midi_to_ngram(midi_seq):
    midi_seq[1:] = [midi_seq[i]-midi_seq[i-1]
        for i in range (1, len(midi_seq))]
    midi_seq[0] = 0
    ngram = ' '.join(map(str, midi_seq))
    return ngram
