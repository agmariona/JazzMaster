import argparse
from matplotlib import pyplot as plt
from matplotlib import ticker
import numpy as np
from scipy.stats import mode
from datetime import datetime

import util.constants as c
import util.tests as t

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', action='store_true', help='run histograms')
parser.add_argument('data_input', type=str, help='path to input data')
parser.add_argument('data_result', type=str, help='path to result data')
parser.add_argument('-b', type=int, default=120, help='bpm')
parser.add_argument('-v', type=str, default='mid', help='volume')
parser.add_argument('-m', action='store_true', help='run harmonic')
parser.add_argument('-r', action='store_true', help='run rhythmic')
parser.add_argument('-d', action='store_true', help='run harmonic dist')
args = parser.parse_args()

NEARBYS = {120: 0.6, 40: 1.5, 240: 0.4, 60: 1.5}
OVERLAPS = {120: 0.4, 40: 1.0, 240: 0.2, 60: 0.9}
VOLS = {'soft': 'Quiet', 'mid': 'Medium', 'loud': 'Loud'}

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

def harmonic_dist():
    ref_scores = []
    exp_scores = []
    songs = c.reference_songs
    bin_size = 0.05
    box_y = 4

    for song in songs:
        ref_scores.append(1-t.harmonic_test(c.PROJ_PATH +
            f'data/reference_transcriptions/{song}'))
        exp_scores.append(1-t.harmonic_test(c.PROJ_PATH +
            f'data/test_transcriptions/trial_1/{song}'))

    mean_ref = np.mean(ref_scores)
    mean_exp = np.mean(exp_scores)
    var_ref = np.var(ref_scores)
    var_exp = np.var(exp_scores)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
    ax1.set_title('Reference Harmonic Correctness Scores')
    ax1.text(0.03, 0.75, f'Mean: {mean_ref:.3f}\nVar: {var_ref:.3f}',
        bbox=dict(facecolor='white', lw=0.8), transform=ax1.transAxes)
    ax1.hist(ref_scores, bins=np.arange(0,1.0+bin_size,bin_size), color='g',
        rwidth=0.9)
    ax1.set_ylabel('Count')

    ax2.set_title('Experimental Harmonic Correctness Scores')
    ax2.text(0.03, 0.75, f'Mean: {mean_exp:.3f}\nVar: {var_exp:.3f}',
        bbox=dict(facecolor='white', lw=0.8), transform=ax2.transAxes)
    ax2.hist(exp_scores, bins=np.arange(0,1.0+bin_size,bin_size), color='b',
        rwidth=0.9)
    ax2.set_ylabel('Count')
    ax2.set_xlabel('Correctness Score')
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(0.1))

    fig.tight_layout()
    plt.show()

def harmonic_hist():
    ref_scores = []
    scores = []
    songs = c.reference_songs
    labels = c.reference_song_names
    for song in songs:
        ref_scores.append(1-t.harmonic_test(c.PROJ_PATH +
            f'data/reference_transcriptions/{song}'))
        scores.append(1-t.harmonic_test(c.PROJ_PATH +
            f'data/test_transcriptions/{song}'))

    fig, ax = plt.subplots()
    x = np.arange(len(songs))
    width = 0.3
    ax.set_title('Harmonic Correctness Scores across 20 Songs')
    ax.plot(np.arange(-1, len(songs)+1), [0.9 for i in range(len(x)+2)],
        color='r')
    ax.bar(x - width/2, ref_scores, width, label='Reference Scores',
        color='b')
    ax.bar(x + width/2, scores, width, label='Test Scores',
        color='g')
    ax.set_ylabel('Correctness Score')
    ax.set_xlim([-1, len(songs)])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.04, 0.5), loc='center left')

    fig.tight_layout()
    fig.set_size_inches(15, 5)
    plt.show()

def rhythmic_hist():
    ref_scores = []
    scores = []
    songs = c.reference_songs
    labels = c.reference_song_names
    for song in songs:
        ref_scores.append(1-t.rhythmic_test(c.PROJ_PATH +
            f'data/reference_transcriptions/{song}'))
        scores.append(1-t.rhythmic_test(c.PROJ_PATH +
            f'data/test_transcriptions/{song}'))

    fig, ax = plt.subplots()
    x = np.arange(len(songs))
    width = 0.3
    ax.set_title('Rhythmic Correctness Scores across 20 Songs')
    ax.plot(np.arange(-1, len(songs)+1), [0.9 for i in range(len(x)+2)],
        color='r')
    ax.bar(x - width/2, ref_scores, width, label='Reference Scores',
        color='b')
    ax.bar(x + width/2, scores, width, label='Test Scores',
        color='g')
    ax.set_ylabel('Correctness Score')
    ax.set_xlim([-1, len(songs)])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.04, 0.5), loc='center left')

    fig.tight_layout()
    fig.set_size_inches(15, 5)
    plt.show()


if __name__ == '__main__':
    if args.h:
        n_trials = 20
        tempos = [40, 120, 240]
        volumes = ['mid', 'loud']

        correct_ratios = [[] for i in range(6)]
        incorrect_ratios = [[] for i in range(6)]

        for k in range(3):
            for j in range(2):
                for i in range(n_trials):
                    input_path = f'data/sweeps/{tempos[k]}_{volumes[j]}_ref_{i}.txt'
                    result_path = f'data/sweeps/{tempos[k]}_{volumes[j]}_{i}.txt'
                    i_t, i_n, c_t, c_n, inc_t, inc_n = process_test(input_path,
                        result_path, tempos[k])
                    correct_ratios[k*2+j].append(c_n.size / i_n.size)
                    incorrect_ratios[k*2+j].append(inc_n.size / i_n.size)


        # fig, ax = plt.subplots()
        # labels = ['40 BPM, Medium', '40 BPM, Loud',
        # '120 BPM, Medium', '120 BPM, Loud',
        # '240 BPM, Medium', '240 BPM, Loud']
        # ax.set_title(f'Ratio of Correctly Measured Notes across\n{n_trials} Trials for each Set of Parameters')
        # ax.hist(correct_ratios, label=labels, align='mid', bins=np.arange(0.3,1.1,0.1), histtype='barstacked',
        #     color=['lightcoral', 'darkred', 'lightblue', 'darkblue', 'lightgreen', 'darkgreen'])
        # ax.legend(loc='best')
        # ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
        # ax.set_ylabel('Number of Trials')
        # ax.set_xlabel('Ratio of Correctly Measured Notes to Total Notes')
        # fig.tight_layout()
        # plt.show()

        fig, ax = plt.subplots()
        labels = ['40 BPM, Medium', '40 BPM, Loud',
        '120 BPM, Medium', '120 BPM, Loud',
        '240 BPM, Medium', '240 BPM, Loud']
        ax.set_title(f'Ratio of Incorrectly Measured Notes across\n{n_trials} Trials for each Set of Parameters')
        ax.hist(incorrect_ratios, label=labels, align='mid',
        bins=np.arange(0.1,0.8,0.1), histtype='barstacked',
            color=['lightcoral', 'darkred', 'lightblue', 'darkblue', 'lightgreen', 'darkgreen'])
        ax.legend(loc='best')
        ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
        ax.set_ylabel('Number of Trials')
        ax.set_xlabel('Ratio of Incorrectly Measured Notes to Total Notes')
        fig.tight_layout()
        plt.show()
    elif args.m:
        harmonic_hist()
    elif args.r:
        rhythmic_hist()
    elif args.d:
        harmonic_dist()
    else:
        i_t, i_n, c_t, c_n, inc_t, inc_n = process_test(args.data_input,
            args.data_result, args.b)

        fig, ax = plt.subplots()

        ax.set_title(f'Frequency Sweep at {args.b} BPM, {VOLS[args.v]} Volume')

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

        fig.tight_layout()
        plt.show()
