import numpy as np
import pickle
import threading

import core.beat_tracker as bt
import util.midi_in as midi_in
import util.util as util

events = midi_in.get_input_simple()
pickle.dump(events, open('events.out', 'wb'))

# events_raw = pickle.load(open('events.out', 'rb'))
# events = [(e[0], e[1], round(e[2]-e[1], ndigits=3)) for e in events_raw]
# n = 5
# seqs = [events[i*n:(i+1)*n] for i in range(len(events)//n)]
#
# tracker = bt.BeatTracker()
# for i in range(len(seqs)):
#     tracker.pass_events(seqs[i])
#     print(tracker.get_best_agent())
