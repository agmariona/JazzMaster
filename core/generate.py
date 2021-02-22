import pychord

import util.util as util
import util.constants as c

track_hypothesis = None
pos_hypothesis = 0

def generate_harmony(matches, initial):
    global track_hypothesis, pos_hypothesis
    print(f"Current hypothesis: {track_hypothesis}")

    t = matches[matches.track == track_hypothesis]
    if not t.empty:
        p = t[t.position == (pos_hypothesis + c.N_NGRAM)]
        if p.empty:
            r = t.iloc[0]
        else:
            r = p.iloc[0]
        pos_hypothesis = r.position
    else:
        r = matches.iloc[0]
        track_hypothesis = r.track
        pos_hypothesis = r.position

    duration = r.duration.split()

    harmony = [pychord.Chord(h) for h in r.harmony.split()]
    delta = (initial - util.note_to_midi(harmony[0].root + '4')) % 12
    # for i in range(len(harmony)):
    #     harmony[i].transpose(delta)

    return harmony, duration

