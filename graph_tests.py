import argparse
from matplotlib import pyplot as plt
from matplotlib import ticker
import numpy as np
from datetime import datetime

import util.constants as c

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', nargs=2, type=str, help='run_histograms')
parser.add_argument('data_input', type=str, help='path to input data')
parser.add_argument('data_result', type=str, help='path to result data')
parser.add_argument('-b', type=int, default=120, help='path to result data')
args = parser.parse_args()

NEARBYS = {120: 0.6, 40: 1.5, 240: 0.4}
OVERLAPS = {120: 0.4, 40: 1.0, 240: 0.2}


def process_test(data_input, data_result, bpm):
    input_notes = np.array([])
    input_times = np.array([])
    correct_notes = np.array([])
    correct_times = np.array([])
    incorrect_notes = np.array([])
    incorrect_times = np.array([])

    with open(c.PROJ_PATH+data_input) as f:
        for line in f:
            label, note, time = line.split()
            time = datetime.strptime(time, "%H:%M:%S.%f")
            if label == 'NOTE':
                input_notes = np.append(input_notes, c.FREQS[note])
                input_times = np.append(input_times, time)

    start_time = input_times[0]

    input_times = np.array([(time - start_time).total_seconds()
        for time in input_times[:-1]])
    input_notes = input_notes[:-1]

    with open(c.PROJ_PATH+data_result) as f:
        for line in f:
            label, note, time = line.split()
            time = (datetime.strptime(time, "%H:%M:%S.%f") - \
                start_time).total_seconds()
            if label == 'NOTE':
                nearby_times = np.array(np.abs(input_times - time) <
                    NEARBYS[bpm])
                overlap_times = np.array(np.abs(correct_times - time) <
                    OVERLAPS[bpm])
                if input_times[nearby_times].size > 0 and \
                    c.FREQS[note] in input_notes[nearby_times] and \
                    c.FREQS[note] not in correct_notes[overlap_times]:
                    correct_notes = np.append(correct_notes, c.FREQS[note])
                    correct_times = np.append(correct_times, time)
                else:
                    incorrect_notes = np.append(incorrect_notes, c.FREQS[note])
                    incorrect_times = np.append(incorrect_times, time)

    return input_times, input_notes, correct_times, correct_notes, \
        incorrect_times, incorrect_notes

if __name__ == '__main__':
    if args.h:
        tempo = int(args.h[0])
        volume = args.h[1]
        n_trials = 20

        correct_ratios = np.array([])
        incorrect_ratios = np.array([])

        for i in range(n_trials):
            input_path = f'data/sweeps/{tempo}_{volume}_ref_{i}.txt'
            result_path = f'data/sweeps/{tempo}_{volume}_{i}.txt'
            i_t, i_n, c_t, c_n, inc_t, inc_n = process_test(input_path,
                result_path, tempo)
            correct_ratios = np.append(correct_ratios, c_n.size / i_n.size)
            incorrect_ratios = np.append(incorrect_ratios, inc_n.size / i_n.size)

        print(correct_ratios)
        print(incorrect_ratios)
    else:
        i_t, i_n, c_t, c_n, inc_t, inc_n = process_test(args.data_input,
            args.data_result, args.b)

        fig, ax = plt.subplots()

        # ax.set_title('Frequency Sweep at 240 BPM')

        ax.scatter(i_t, i_n/1e3, marker='o', color='k', label='Input Notes')
        ax.scatter(c_t, c_n/1e3, marker='o', color='b', label='Correctly Measured Notes')
        ax.scatter(inc_t, inc_n/1e3, marker='x', color='r',
            label='Incorrectly Measured Notes')
        ax.legend(loc='best')

        ax.set_xlabel('Time (s)')

        ax.set_yscale('log')
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax.yaxis.set_minor_formatter(ticker.FormatStrFormatter('%.1f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
        ax.set_ylabel('Frequency (kHz)')

        plt.tight_layout()
        plt.show()
