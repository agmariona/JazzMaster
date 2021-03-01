import argparse

import util.constants as c
import util.tests as t

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-l', action='store_true', help='run listen tests')
parser.add_argument('-h', type=str, help='run harmonic test')
parser.add_argument('-r', type=str, help='run rhythmic test')
parser.add_argument('--harmref', action='store_true',
    help='harmonic reference')
parser.add_argument('--rhythmref', action='store_true',
    help='rhythmic reference')
parser.add_argument('-n', nargs=2, type=str, help='run note tests with paths')
args = parser.parse_args()

sweep = open(c.PROJ_PATH+'/library/txt/test_sweep.txt')

if args.l:
    t.listen_test(sweep, args.b)

if args.h:
    t.harmonic_test(args.h)

if args.r:
    t.rhythmic_test(args.r)

if args.n:
    t.note_test(args.n[0], args.n[1])

if args.harmref:
    t.harmonic_reference_test()

if args.rhythmref:
    t.rhythmic_reference_test()
