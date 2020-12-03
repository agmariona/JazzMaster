track_hypothesis = None

def generate_harmony(matches):
    global track_hypothesis
    s = matches[matches.track == track_hypothesis]
    if not s.empty:
        r = s.sample().squeeze()
    else:
        r = matches.sample().squeeze()
        track_hypothesis = r.track

    harmony = r.harmony.split()
    duration = list(map(float, r.duration.split()))
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
