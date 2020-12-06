import fractions

import util.util as util
import util.constants as c

track_hypothesis = None
pos_hypothesis = 0

def generate_harmony(matches):
    global track_hypothesis, pos_hypothesis

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

    harmony = r.harmony.split()
    duration = [util.duration_to_sec(
        float(fractions.Fraction(d)), track_bpms[track_hypothesis])
        for d in r.duration.split()]
    harmony, duration = squeeze_harmony(harmony, duration)

    return harmony, duration

def squeeze_harmony(harmony, duration):
    squeezed_harmony, squeezed_duration = [], []
    prev_chord, running_duration = harmony[0], duration[0]
    for i in range(1, len(harmony)):
        if harmony[i] == prev_chord:
            running_duration += duration[i]
        else:
            squeezed_harmony.append(prev_chord)
            squeezed_duration.append(running_duration)
            prev_chord, running_duration = harmony[i], duration[i]
    squeezed_harmony.append(prev_chord)
    squeezed_duration.append(running_duration)
    return squeezed_harmony, squeezed_duration

track_bpms = {
    'take_the_a_train': 160,
    'misty': 65,
    'satin_doll': 120
}
