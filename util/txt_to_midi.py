import argparse
from fractions import Fraction
import mido

from compare_helpers import *

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('txt', type=str, help='path to .txt to convert')
args = parser.parse_args()

txt = open(args.txt)

bpm, time_sig = txt.readline().split('/')
bpm = int(bpm)
tempo = mido.bpm2tempo(bpm)
beat_unit = int(time_sig.split(':')[0])
ticks_per_beat = 10000

mid = mido.MidiFile()
mid.ticks_per_beat = ticks_per_beat
track = mido.MidiTrack()
mid.tracks.append(track)
track.append(mido.MetaMessage('set_tempo', tempo=tempo))

notes = list()
for line in txt:
    note, duration, chord = line.split()
    duration = float(Fraction(duration))
    notes.append([note_txt_to_midi(note),
        duration_txt_to_midi(duration, ticks_per_beat, bpm, tempo)])

rest_buffer = 0
for note, ticks in notes:
    if note == 0:
        rest_buffer = ticks
        continue
    track.append(mido.Message('note_on', note=note, velocity=64,
        time=0+rest_buffer))
    track.append(mido.Message('note_off', note=note, velocity=64,
        time=ticks))
    rest_buffer = 0

mid.save(f'{args.txt[:-4]}.mid')
