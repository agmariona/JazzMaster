import stopwatch
from pychord import Chord
import threading
from time import sleep

import compare
import generate
import play

note_buffer = list()
duration_buffer = list()
seq_ready = False
seq_cv = threading.Condition()

keys_to_notes = {
    'a': 'CN4',
    's': 'C#4',
    'd': 'DN4',
    'f': 'D#4',
    'g': 'EN4',
    'h': 'FN4',
    'j': 'F#4',
    'k': 'GN4',
    'l': 'G#4',
    ';': 'AN4',
    '\'': 'A#4',
    '/': 'BN4',
    'q': 'CN5',
    'w': 'C#5',
    'e': 'DN5',
    'r': 'D#5',
    't': 'EN5',
    'y': 'FN5',
    'u': 'F#5',
    'i': 'GN5',
    'o': 'G#5',
    'p': 'AN5',
    '[': 'A#5',
    ']': 'BN5'
}

def get_input():
    global seq_ready

    note_timer = stopwatch.Stopwatch()
    current_note = None
    while True:
        key = input()
        try:
            note = keys_to_notes[key]
            if current_note:
                note_timer.stop()
                note_buffer.append(current_note)
                duration = round(note_timer.duration, ndigits=2)
                duration_buffer.append(duration)
                note_timer.reset()
                play.note_off(current_note)
            current_note = note
            note_timer.start()
            play.note_on(note)
        except KeyError:
            if key == ' ':
                if current_note:
                    note_timer.stop()
                    note_buffer.append(current_note)
                    duration = round(note_timer.duration, ndigits=2)
                    duration_buffer.append(duration)
                    note_timer.reset()
                    play.note_off(note)
                current_note = None
        with seq_cv:
            if len(note_buffer) >= 5:
                seq_ready = True
                seq_cv.notify()

print('Ready.')
threading.Thread(target=get_input).start()

while True:
    with seq_cv:
        while not seq_ready:
            seq_cv.wait()
        seq, note_buffer = note_buffer[:5], note_buffer[5:]
        duration, duration_buffer = duration_buffer[:5], duration_buffer[5:]
        seq_ready = False

    matches = compare.get_matches(seq)
    harmony, duration = generate.generate_harmony(matches)
    threading.Thread(target=play.play_progression,
        args=(harmony, duration)).start()
