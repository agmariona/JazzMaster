import mido
import stopwatch

import util.constants as c

input_buffer = []
timer = stopwatch.Stopwatch()
current_note = None

def get_input(pass_buffer, pass_ready, pass_cv):
    global input_buffer
    with mido.open_input() as inport:
        for msg in inport:
            if msg.type == 'note_on':
                if current_note:
                    stop_note(current_note)
                start_note(msg.note)
            elif msg.type == 'note_off':
                if msg.note == current_note:
                    stop_note(current_note)
            with pass_cv:
                if len(input_buffer) >= c.N_NGRAM:
                    pass_buffer[:] = input_buffer[:c.N_NGRAM]
                    input_buffer = input_buffer[c.N_NGRAM:]
                    pass_ready[0] = True
                    pass_cv.notify()

def stop_note(note):
    global current_note
    timer.stop()
    duration = round(timer.duration, ndigits=2)
    input_buffer.append((note, duration))
    current_note = None
    timer.reset()

def start_note(note):
    global current_note
    current_note = note
    timer.start()
