import numpy as np
import pickle
import stopwatch
import threading

import core.play as play
import core.beat_tracker as bt
import util.midi_in as midi_in
import util.util as util

# events = midi_in.get_input_simple()
# pickle.dump(events, open('events.out', 'wb'))

# events_raw = pickle.load(open('events.out', 'rb'))
# events = [(e[0], e[1], round(e[2]-e[1], ndigits=3)) for e in events_raw]
# n = 5
# seqs = [events[i*n:(i+1)*n] for i in range(len(events)//n)]

# for i in range(len(seqs)):
#     tracker.pass_events(seqs[i])
#     print(tracker.get_best_agent())

pass_buffer = []
pass_ready = [False]
pass_cv = threading.Condition()

clock = stopwatch.Stopwatch()
clock.start()

print('BeatTracker online.')
threading.Thread(target=midi_in.get_input,
    args=(pass_buffer, pass_ready, pass_cv, clock)).start()
threading.Thread(target=play.click, args=(clock,)).start()
tracker = bt.BeatTracker()

while True:
    with pass_cv:
        while not pass_ready[0]:
            pass_cv.wait()
        seq = pass_buffer[:]
        pass_ready[0] = False

    events = [(e[0], e[1], round(e[2]-e[1], ndigits=3)) for e in seq]
    tracker.pass_events(events)
    print(tracker.get_best_agent())
    play.update_tempo(*tracker.get_tempo_phase())
