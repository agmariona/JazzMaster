"""TS5"""
import argparse
import matplotlib.pyplot as plt
import numpy as np
import queue
import sounddevice as sd
import sys
import scipy.signal as signal
import select
from scipy.fft import rfft, rfftfreq

import util.constants as c

SAVE_PATH = '/Users/agm/Documents/Harvard/ENG-SCI 100/JazzMaster/data/'

DQ = queue.Queue()

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

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    if any(indata):
        magnitude = np.abs(rfft(indata[:, 0], n=c.FFT_N))
        DQ.put(magnitude)

def plot_magnitude(magnitude, freqs):
    peak_freq, peak_magnitude = get_peak_freq(magnitude, freqs)

    fig, ax1 = plt.subplots()
    ax1.set_title('FFT Magnitude')
    ax1.plot(freqs, magnitude, color='b')
    if peak_freq:
        ax1.scatter(peak_freq, peak_magnitude, color='r')
    ax1.set_ylabel('Magnitude')
    ax1.set_xlabel('Frequency (Hz)')
    plt.show()

def display_magnitude(magnitude, freqs, pitch):
    peak_freq, peak_magnitude = get_peak_freq(magnitude, freqs)

    fig, ax1 = plt.subplots()
    ax1.set_title(f'FFT Magnitude')
    ax1.plot(freqs, magnitude, color='b')
    if peak_freq:
        ax1.scatter(peak_freq, peak_magnitude, color='r')
    ax1.set_ylabel('Magnitude')
    ax1.set_xlabel('Frequency (Hz)')
    plt.show(block=False)
    plt.pause(1)
    plt.close()

def plot_energy(energy):
    fig, ax_energy = plt.subplots()
    ax_energy.set_title('Weighted Energy')
    ax_energy.plot(np.arange(energy.size*c.WIN_LEN/c.F_SAMP,
        step=c.WIN_LEN/c.F_SAMP), energy, color='g')
    ax_energy.set_ylabel('Energy')
    ax_energy.set_xlabel('Time (s)')
    plt.show()

def plot_onsets(energy_history, onsets):
    time = np.arange(energy_history.size*c.WIN_LEN/c.F_SAMP, step=c.WIN_LEN/c.F_SAMP)
    fig, ax_energy = plt.subplots()
    ax_energy.set_title('Weighted Energy')
    ax_energy.plot(time[:energy_history.size], energy_history, color='g')
    ax_energy.scatter(time[onsets], energy_history[onsets], color='r')
    ax_energy.set_ylabel('Energy')
    ax_energy.set_xlabel('Time (s)')
    plt.show()

def get_peak_freq(magnitude, freqs):
    magnitude = smooth_curve(magnitude)
    peaks = signal.find_peaks(magnitude, height=0.5, prominence=0.7)[0]
    if peaks.size == 0:
        return None, 0
    max_peak = peaks[np.argmax(magnitude[peaks])]
    max_peak = peaks[0]
    return freqs[max_peak], magnitude[max_peak]

def find_closest(value, targets):
    i = np.searchsorted(targets, value)
    # Clip and adjust for edge cases
    i = np.clip(i, 1, len(targets)-1)
    i -= value - targets[i-1] < targets[i] - value
    return targets[i]

def smooth_curve(data):
    N, Wn = signal.buttord(0.1, 0.3, 0.5, 40)
    sos = signal.butter(N, Wn, output='sos')
    return signal.sosfiltfilt(sos, data)

def smooth_energy(energy):
    return energy
    N, Wn = signal.buttord(0.3, 0.4, 0.5, 40)
    sos = signal.butter(N, Wn, output='sos')
    return signal.sosfiltfilt(sos, energy)

def get_next_note():
    peak_freq = None
    data = DQ.get()
    peak_freq, peak_magnitude = get_peak_freq(data, FFT_FREQS)
    if not peak_freq:
        return None, 0, 0, data
    note_freq = find_closest(peak_freq, list(FREQS.values()))
    note = NOTES[note_freq]
    return note, peak_freq, peak_magnitude, data

def is_octave(pitch_a, pitch_b):
    if len(pitch_a) == 3:
        principal_a = pitch_a[:2]
    else:
        principal_a = pitch_a[:1]

    if len(pitch_b) == 3:
        principal_b = pitch_b[:2]
    else:
        principal_b = pitch_b[:1]

    if principal_a == principal_b:
        return True
    else:
        return False

def detect_onset(data, energy_history, onsets):
    new_energy = (1/(FFT_N/2+1)) * np.sum(np.arange(FFT_N/2+1)*(data**2))
    energy_history = np.append(energy_history, new_energy)
    onsets = signal.find_peaks(smooth_energy(energy_history), height=8,
        prominence=8)[0]
    return energy_history, onsets

if __name__ == '__main__':
    notes = list()
    current_note = {'pitch': None, 'duration': 0, 'magnitude': 0}
    last_printed_data = None
    energy_history = np.empty((0,))
    pitch_history = np.array((0,))
    data_history = np.empty((0,FFT_N//2+1))
    onsets = np.empty((0,), dtype=int)

    with sd.InputStream(device=args.device, channels=1, callback=callback,
                        blocksize=WIN_LEN, samplerate=F_SAMP):
        while True:
            pitch, freq, magnitude, data = get_next_note()
            pitch_history = np.append(pitch_history, pitch)
            data_history = np.append(data_history, data.reshape(-1,FFT_N//2+1),
                axis=0)
            energy_history, onsets = detect_onset(data, energy_history, onsets)
            if energy_history.shape[0] == 150:
                plot_onsets(smooth_energy(energy_history), onsets)
                np.save(SAVE_PATH+'energy2',  energy_history, allow_pickle=True)
                np.save(SAVE_PATH+'pitch2',  pitch_history, allow_pickle=True)
                np.save(SAVE_PATH+'data2',  data_history, allow_pickle=True)
                np.save(SAVE_PATH+'onsets2',  onsets, allow_pickle=True)
                sys.exit()

            # energy_history, onset = detect_onset(data, energy_history)
            # if onset:
            #     print(f'{pitch}, {FREQS[pitch]}, {freq}')

            # if onset and pitch:
            #     # New note

            #     print(pitch, FREQS[pitch], freq)
            #     plot_energy(energy_history)

            #     notes.append(current_note)
            #     current_note['pitch'] = pitch
            #     current_note['magnitude'] = magnitude
            #     current_note['duration'] = UNIT_DURATION
            # if pitch and not onset:
            #     # Same note
            #     current_note['duration'] += UNIT_DURATION
            # if not pitch:
            #     if current_note['pitch']:
            #         # End note
            #         print('END NOTE')
            #         notes.append(current_note)
            #         current_note['pitch'] = None
            #         current_note['magnitude'] = 0
            #         current_note['duration'] = 0
