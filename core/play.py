import fluidsynth
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
