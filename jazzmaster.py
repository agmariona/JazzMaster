import argparse
import stopwatch
import threading
import sounddevice as sd

import core.listen as listen
import core.compare as compare
import core.generate as generate
import core.play as play
import core.beat_tracker as bt
import util.midi_in as midi_in
import util.util as util

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-d', '--device', type=int, help='input device (numeric ID)', default=0)
parser.add_argument('-m', action='store_true', help='MIDI input')
parser.add_argument('-c', action='store_true', help='metronome click')
args = parser.parse_args(remaining)

pass_buffer = []
pass_ready = [False]
pass_cv = threading.Condition()

clock = stopwatch.Stopwatch()
clock.start()

if args.m:
    threading.Thread(target=midi_in.get_input,
            args=(pass_buffer, pass_ready, pass_cv, clock)).start()
else:
    threading.Thread(target=listen.get_input,
        args=(args.device, pass_buffer, pass_ready, pass_cv)).start()
threading.Thread(target=play.player).start()
if args.c:
    threading.Thread(target=play.click, args=(clock,)).start()
tracker = bt.BeatTracker()
print("JazzMaster online.")

while True:
    ### LISTEN #####
    with pass_cv:
        while not pass_ready[0]:
            pass_cv.wait()
        seq = pass_buffer[:]
        pass_ready[0] = False
    events = [(e[0], e[1], round(e[2]-e[1], ndigits=3)) for e in seq]
    notes, onsets, durations = util.unzip_sequence(events)
    initial = notes[0]
    print(events)
    ################

    ### COMPARE ####
    matches, next_matches = compare.get_matches(notes)
    ################

    ### GENERATE ###
    harmony, duration = generate.generate_harmony(
        matches, next_matches, initial)
    # print(f"\t{harmony}")
    ################

    ### PLAY #######
    tracker.pass_events(events)
    print(f"\t{tracker.get_best_agent()}")
    play.update_tempo(*tracker.get_tempo_phase())
    threading.Thread(target=play.push_progression,
        args=(harmony, duration)).start()
    ################
