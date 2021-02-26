import argparse
from matplotlib import pyplot as plt
from matplotlib import ticker
import numpy as np
from datetime import datetime

import util.constants as c

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('data_input', type=str, help='path to input data')
parser.add_argument('data_result', type=str, help='path to result data')
args = parser.parse_args()

input_notes = np.array([])
input_times = np.array([])
result_notes = np.array([])
result_times = np.array([])

with open(c.PROJ_PATH+args.data_input) as f:
    for line in f:
        label, note, time = line.split()
        if label == 'NOTE':
            input_notes = np.append(input_notes, c.FREQS[note])
            input_times = np.append(input_times,
                datetime.strptime(time, "%H:%M:%S.%f"))

with open(c.PROJ_PATH+args.data_result) as f:
    for line in f:
        label, note, time = line.split()
        if label == 'NOTE':
            result_notes = np.append(result_notes, c.FREQS[note])
            result_times = np.append(result_times,
                datetime.strptime(time, "%H:%M:%S.%f"))

input_deltas = np.array([(time - input_times[0]).total_seconds()
    for time in input_times[:-1]])
result_deltas = np.array([(time - input_times[0]).total_seconds()
    for time in result_times])

input_notes = input_notes[:-1]

fig, ax = plt.subplots()

# ax.set_title('Frequency Sweep at 240 BPM')

ax.scatter(input_deltas, input_notes/1e3, marker='o', color='b',
    label='Input Signal')
ax.scatter(result_deltas, result_notes/1e3, marker='o', color='r',
    label='Measured Signal')
ax.legend(loc='best')

ax.set_xlabel('Time (s)')

ax.set_yscale('log')
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
ax.yaxis.set_minor_formatter(ticker.FormatStrFormatter('%.1f'))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
ax.set_ylabel('Frequency (kHz)')

plt.tight_layout()
plt.show()
