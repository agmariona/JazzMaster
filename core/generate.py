import pychord

import util.util as util
import util.constants as c

track_hypothesis = None
pos_hypothesis = 0

def generate_harmony(matches, next_matches, initial):
    global track_hypothesis, pos_hypothesis
    # print(f"Current hypothesis: {track_hypothesis}:{pos_hypothesis}")

    track_matches = matches[matches.track == track_hypothesis]
    if not track_matches.empty:
        pos_matches = track_matches[track_matches.position == pos_hypothesis]
        if pos_matches.empty:
            prev_match = track_matches.iloc[0]
        else:
            prev_match = pos_matches.iloc[0]
        result = next_matches[next_matches.track.isin([prev_match.track]) &
            next_matches.position.isin([prev_match.position +
            c.N_NGRAM])].iloc[0]
        pos_hypothesis = result.position
    else:
        prev_match = matches.iloc[0]
        result = next_matches.iloc[0]
        track_hypothesis = result.track
        pos_hypothesis = result.position

    duration = result.duration.split()
    harmony = [pychord.Chord(h) for h in result.harmony.split() if h != 'None']
    delta = (initial - prev_match.initial) % 12
    for i in range(len(harmony)):
        harmony[i].transpose(delta)

    return harmony, duration

