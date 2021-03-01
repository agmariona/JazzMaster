import argparse

import util.constants as c
import util.tests as t

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-l', type=int, help='run listen tests at tempo')
parser.add_argument('-h', type=str, help='run harmonic test')
parser.add_argument('-r', type=str, help='run rhythmic test')
parser.add_argument('-c', nargs='*', type=str,
    help='run both correctness tests')
parser.add_argument('--harmref', action='store_true',
    help='harmonic reference')
parser.add_argument('--rhythmref', action='store_true',
    help='rhythmic reference')
parser.add_argument('-n', nargs=2, type=str, help='run note tests with paths')
args = parser.parse_args()

sweep = open(c.PROJ_PATH+'/library/txt/test_sweep.txt')

if args.l:
    t.listen_test(sweep, args.l)

if args.h:
    print("Harmonic correctness:", end='')
    t.harmonic_test(args.h)

if args.r:
    print("Rhythmic correctness:", end='')
    t.rhythmic_test(args.r)

if args.c:
    for arg in args.c:
        print(f"{arg}:")
        print("\tHarmonic correctness:", end='')
        t.harmonic_test(arg)
        print("\tRhythmic correctness:", end='')
        t.rhythmic_test(arg)

if args.n:
    t.note_test(args.n[0], args.n[1])

if args.harmref:
    t.harmonic_reference_test()

if args.rhythmref:
    t.rhythmic_reference_test()
