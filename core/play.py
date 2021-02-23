import fluidsynth
import fractions
import math
import numpy as np
import pychord
import simpleaudio as sa
import threading
from time import sleep

import util.util as util
import util.constants as constants

fs = [fluidsynth.Synth() for i in range(2)]
for f in fs:
    f.start()
    sfid = f.sfload("resources/soundfont.sf2")
    f.program_select(0, sfid, 0, 0)

def play_chord(chord, root_pitch, duration):
    global async_playing, async_notes
    if async_playing:
        for note in async_notes:
            fs[0].noteoff(0, note)
        async_playing = False
    components = chord.components_with_pitch(root_pitch)
    notes = util.sequence_to_midi(components)
    for note in notes:
        fs[0].noteon(0, note, 80)
    sleep(duration)
    for note in notes:
        fs[0].noteoff(0, note)

async_playing = False
async_notes = list()

def play_chord_async(chord, root_pitch):
    global async_playing, async_notes
    if async_playing:
        for note in async_notes:
            fs[0].noteoff(0, note)
    async_playing = True
    components = chord.components_with_pitch(root_pitch)
    async_notes = util.sequence_to_midi(components)
    for note in async_notes:
        fs[0].noteon(0, note, 80)

harmony_buffer = []
harmony_available = False
harmony_cv = threading.Condition()

def push_progression(harmony, durations):
    global harmony_buffer, harmony_available
    durations = [util.duration_to_sec(float(fractions.Fraction(d)), tempo)
        for d in durations]
    harmony, durations = squeeze_harmony(harmony, durations)
    with harmony_cv:
        harmony_buffer = [(c, 3, d) for c, d in zip(harmony, durations)]
        harmony_available = True
        harmony_cv.notify()

def player():
    global harmony_available
    while True:
        with harmony_cv:
            while not harmony_available:
                harmony_cv.wait()
        while len(harmony_buffer) > 0:
            with harmony_cv:
                chord = harmony_buffer.pop(0)
            print(f"\tPlaying {chord[0]} for {chord[2]:.02} seconds")
            if len(harmony_buffer) > 0:
                play_chord(*chord)
            else:
                play_chord_async(chord[0], chord[1])
        harmony_available = False

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

def note_on(note):
    if type(note) == str:
        note = util.note_to_midi(note)
    fs[1].noteon(0, note, 127)

def note_off(note):
    if type(note) == str:
        note = util.note_to_midi(note)
    fs[1].noteoff(0, note)

ibi = None
tempo = None
phase = None

def update_tempo(new_ibi, new_phase):
    global ibi, tempo, phase
    ibi = new_ibi
    tempo = 1.0/ibi*60
    phase = new_phase

def click(clock):
    click_noise = sa.WaveObject.from_wave_file(
        constants.PROJ_PATH + 'resources/click.wav')
    while not ibi:
        pass
    while True:
        next_beat = \
            util.nearest_multiple_above(ibi, clock.duration - phase) + phase
        sleep(next_beat - clock.duration)
        click_noise.play().wait_done()


