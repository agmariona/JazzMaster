import fluidsynth
import pychord
from time import sleep

import util.util as util

fs = [fluidsynth.Synth() for i in range(2)]
for f in fs:
    f.start()
    sfid = f.sfload("resources/soundfont.sf2")
    f.program_select(0, sfid, 0, 0)

def play_chord(f, chord, root_pitch, duration):
    components = chord.components_with_pitch(root_pitch)
    notes = util.sequence_to_midi(components)
    for note in notes:
        f.noteon(0, note, 127)
    sleep(duration)
    for note in notes:
        f.noteoff(0, note)

def play_progression(harmony, durations):
    chords = [pychord.Chord(c) for c in harmony]
    for c, d in zip(chords, durations):
        play_chord(fs[0], c, 3, d)

def note_on(note):
    if type(note) == str:
        note = util.note_to_midi(note)
    fs[1].noteon(0, note, 127)

def note_off(note):
    if type(note) == str:
        note = util.note_to_midi(note)
    fs[1].noteoff(0, note)
