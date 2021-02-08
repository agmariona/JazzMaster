import mido
import stopwatch

import util.constants as c

input_buffer = []
timer = stopwatch.Stopwatch()
start_time = 0
stop_time = 0
current_note = None

def get_input(pass_buffer, pass_ready, pass_cv, clock):
    global input_buffer
    with mido.open_input() as inport:
        timer.start()
        for msg in inport:
            if msg.type == 'note_on':
                if current_note:
                    stop_note(current_note, clock)
                start_note(msg.note, clock)
            elif msg.type == 'note_off':
                if msg.note == current_note:
                    stop_note(current_note, clock)
            with pass_cv:
                if len(input_buffer) >= c.N_NGRAM:
                    pass_buffer[:] = input_buffer[:c.N_NGRAM]
                    input_buffer = input_buffer[c.N_NGRAM:]
                    pass_ready[0] = True
                    pass_cv.notify()

def get_input_simple():
    global input_buffer
    with mido.open_input() as inport:
        timer.start()
        for msg in inport:
            if msg.type == 'note_on':
                if current_note:
                    stop_note(current_note)
                start_note(msg.note)
            elif msg.type == 'note_off':
                if msg.note == current_note:
                    stop_note(current_note)
            elif msg.type == 'stop':
                break
    return input_buffer

def stop_note(note, clock):
    global current_note, stop_time
    stop_time = clock.duration
    duration = round(start_time-stop_time, ndigits=3)
    input_buffer.append(
        (note, round(start_time, ndigits=3), round(stop_time, ndigits=3)))
    current_note = None

def start_note(note, clock):
    global current_note, start_time
    start_time = clock.duration
    current_note = note
