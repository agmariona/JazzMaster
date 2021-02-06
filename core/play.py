import fluidsynth
import math
import numpy as np
import pychord
from time import sleep

import util.util as util

fs = [fluidsynth.Synth() for i in range(2)]
for f in fs:
    f.start()
    sfid = f.sfload("resources/soundfont.sf2")
    f.program_select(0, sfid, 0, 0)

def play_chord(chord, root_pitch, duration):
    components = chord.components_with_pitch(root_pitch)
    notes = util.sequence_to_midi(components)
    for note in notes:
        fs[0].noteon(0, note, 127)
    sleep(duration)
    for note in notes:
        fs[0].noteoff(0, note)

async_playing = False
async_notes = list()

def play_chord_async(chord, root_pitch):
    chord = pychord.Chord(chord)
    global async_playing, async_notes
    if async_playing:
        for note in async_notes:
            fs[0].noteoff(0, note)
    async_playing = True
    components = chord.components_with_pitch(root_pitch)
    async_notes = util.sequence_to_midi(components)
    for note in async_notes:
        fs[0].noteon(0, note, 127)

def play_progression(harmony, durations):
    chords = [pychord.Chord(c) for c in harmony]
    for c, d in zip(chords, durations):
        play_chord(c, 3, d)

def note_on(note):
    if type(note) == str:
        note = util.note_to_midi(note)
    fs[1].noteon(0, note, 127)

def note_off(note):
    if type(note) == str:
        note = util.note_to_midi(note)
    fs[1].noteoff(0, note)

def cluster_intervals(onset_times):
    d = 0.025
    clusters = []
    averages = []
    for i in range(len(onset_times)):
        for j in range(i+1, len(onset_times)):
            interval = onset_times[j] - onset_times[i]
            if interval < 0.025 or interval > 2.5:
                continue

            try:
                k = np.argmin(np.abs(np.array(averages) - interval))
            except ValueError:
                k = None

            if k is not None and np.abs(averages[k] - interval) < d:
                clusters[k].append(interval)
                averages[k] = np.mean(clusters[k])
            else:
                clusters.append([interval])
                averages.append(interval)

    merged_clusters = []
    deleted = []
    for i in range(len(clusters)):
        if i in deleted:
            continue
        for j in range(i+1, len(clusters)):
            if j in deleted:
                continue
            if np.abs(np.mean(clusters[i]) - np.mean(clusters[j])) < d:
                clusters[i] = clusters[i] + clusters[j]
                deleted.append(j)
        merged_clusters.append(clusters[i])

    return merged_clusters

def nearest_multiple(m, x):
    if m == 0:
        return x
    else:
        return math.floor((x / m) + 0.5) * m

class Agent:
    inner_window = 0.07

    def __init__(self, tempo, phase):
        self.tempo = tempo
        self.phase = phase
        self.confidence = 0

    def receive_event(self, event):
        closest_beat = nearest_mulitple(self.tempo, event - self.phase) \
            + self.phase
        delta = event - closest_beat
        if abs(delta) < inner_window:
            self.confidence += 1

def beat_tracker(init_seq):
    cluster
