import pandas as pd
import util.util as util

db = pd.read_pickle('resources/compare.db')

def get_matches(seq):
    ngram = sequence_to_ngram(seq)
    print(ngram)
    matches = db[db.ngram==ngram]
    if matches.empty:
        print('Error: Match not found. Only exact matching supported.')
        exit(1)

    # Information comes from *next* ngram
    to_drop = []
    for i, r in matches.iterrows():
        if db.iloc[i].track != db.iloc[i+1].track:
            to_drop.append(i)
    matches = matches.drop(to_drop)
    matches = db.iloc[matches.index+1]

    if matches.empty:
        print('Error: End of song.')
        exit(1)

    return matches

def sequence_to_ngram(sequence):
    ngram = util.sequence_to_midi(sequence)
    print(ngram)
    ngram[1:] = [ngram[i]-ngram[i-1] for i in range (1, len(ngram))]
    ngram[0] = 0
    ngram = ' '.join(map(str, ngram))

    return ngram
