import argparse
import numpy as np
import sounddevice as sd
import sys

sys.path.append('..') # path hack
import util.constants as c
import util.listen_helpers as h

input_buffer = []
start_time = 0
stop_time = 0
current_note = None

def get_input(device, pass_buffer, pass_ready, pass_cv, prominence,
    logging):
    global input_buffer
    with sd.InputStream(device=device, channels=1, callback=h.sd_callback,
        blocksize=c.F_WIN_LEN, samplerate=c.F_SAMP):
        while True:
            h.update_hist()
            h.detect_onset(prominence)
            input_buffer += h.load_buffer(logging)
            with pass_cv:
                if len(input_buffer) >= c.N_NGRAM:
                    pass_buffer[:] = input_buffer[:c.N_NGRAM]
                    input_buffer = input_buffer[c.N_NGRAM:]
                    pass_ready[0] = True
                    pass_cv.notify()

if __name__ == '__main__':
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
        '-d', '--device', type=int, help='input device (numeric ID)')
    parser.add_argument('-p', type=int, help='onset prominence', default=2e4)
    args = parser.parse_args(remaining)

    with sd.InputStream(device=args.device, channels=1,
        callback=h.sd_callback, blocksize=c.F_WIN_LEN, samplerate=c.F_SAMP):
        i = 0
        while True:
            h.update_hist()
            h.detect_onset(args.p)
            h.print_pitches()

            # i += 1
            # if (i%15==0):
            #     h.plot_energy_with_onsets()
