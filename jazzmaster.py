import threading

import midi_in
import compare
import generate
import play
import util.util as util

pass_buffer = []
pass_ready = [False]
pass_cv = threading.Condition()

print('Jazzmaster online.')
threading.Thread(target=midi_in.get_input,
    args=(pass_buffer, pass_ready, pass_cv)).start()

while True:
    with pass_cv:
        while not pass_ready[0]:
            pass_cv.wait()
        seq = pass_buffer[:]
        pass_ready[0] = False

    notes, durations = util.unzip_sequence(seq)

    matches = compare.get_matches(notes)
    harmony, duration = generate.generate_harmony(matches)
    print(harmony, duration)
    threading.Thread(target=play.play_progression,
        args=(harmony, duration)).start()
