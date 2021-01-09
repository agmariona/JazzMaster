"""TS5"""
import argparse
import numpy as np
import sounddevice as sd
import sys

sys.path.append('..') # path hack
import util.constants as c
import util.listen_helpers as h

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
    '-d', '--device', type=int,
    help='input device (numeric ID)')
# parser.add_argument(
#     '-b', '--blocksize', type=int, metavar='NSAMP', default=50,
#     help='block size (default %(default) samples)')
# parser.add_argument(
#     '-g', '--gain', type=float, default=10,
#     help='initial gain factor (default %(default)s)')
args = parser.parse_args(remaining)

if __name__ == '__main__':
    with sd.InputStream(device=args.device, channels=1,
        callback=h.sd_callback, blocksize=c.F_WIN_LEN, samplerate=c.F_SAMP):
        i = 0
        while True:
            h.update_hist()
            h.detect_onset()
            h.print_pitches()
            h.save_onsets(5)

            #  i += 1
            # if (i%10==0):
            #     h.plot_energy_with_onsets()
