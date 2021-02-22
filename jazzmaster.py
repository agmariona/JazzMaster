import stopwatch
import threading

import core.compare as compare
import core.generate as generate
import core.play as play
import core.beat_tracker as bt
import util.midi_in as midi_in
import util.util as util

pass_buffer = []
pass_ready = [False]
pass_cv = threading.Condition()

clock = stopwatch.Stopwatch()
clock.start()

print('JazzMaster online.')
threading.Thread(target=midi_in.get_input,
    args=(pass_buffer, pass_ready, pass_cv, clock)).start()
threading.Thread(target=play.player).start()
# threading.Thread(target=play.click, args=(clock,)).start()
tracker = bt.BeatTracker()

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
    ################

    ### COMPARE ####
    matches = compare.get_matches(notes)
    ################

    ### GENERATE ###
    harmony, duration = generate.generate_harmony(matches, initial)
    print(f"\t{harmony}")
    ################

    ### PLAY #######
    tracker.pass_events(events)
    print(f"\t{tracker.get_best_agent()}")
    play.update_tempo(*tracker.get_tempo_phase())
    threading.Thread(target=play.push_progression,
        args=(harmony, duration)).start()
    ################
