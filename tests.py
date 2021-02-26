import argparse

import util.constants as c
import util.tests as tests

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-l', action='store_true', help='run listen tests')
parser.add_argument('-h', action='store_true', help='run harmonic tests')
parser.add_argument('-n', nargs=2, type=str, help='run note tests with paths')
parser.add_argument('-b', type=int, default=120, help='bpm')
args = parser.parse_args()

sweep = open(c.PROJ_PATH+'/library/txt/test_sweep.txt')

if args.l:
    tests.listen_test(sweep, args.b)

if args.h:
    tests.harmonic_test(args.b)

if args.n:
    tests.note_test(args.n[0], args.n[1])
