import matplotlib.pyplot as plt
import numpy as np
import queue
from scipy import fft, signal

import util.constants as c

SAVE_PATH = '/Users/agm/Documents/Harvard/ENG-SCI 100/JazzMaster/data/'

pitch_dq = queue.Queue()
onset_dq = queue.Queue()

rfft_hist = np.empty((0, c.RFFT_N), dtype=float)
pitch_hist = np.empty((0,), dtype=str)
freq_hist = np.empty((0,), dtype=float)
magn_hist = np.empty((0,), dtype=float)
energy_hist = np.empty((0,), dtype=float)
onset_hist = np.empty((0,), dtype=int)

### Plotters ###

def plot_pitch(rfft, pitch, freq, magn):
    fig, ax = plt.subplots()
    ax.plot(c.RFFT_FREQS, rfft, color='b')
    ax.scatter(freq, magn, color='r')
    ax.set_title(f'RFFT Magnitude ({pitch})')
    ax.set_ylabel('Magnitude')
    ax.set_xlabel('Frequency (Hz)')
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

def splot_pitch(rfft, pitch, freq, magn, fname):
    fig, ax = plt.subplots()
    ax.plot(c.RFFT_FREQS, rfft, color='b')
    ax.scatter(freq, magn, color='r')
    ax.set_title(f'RFFT Magnitude ({pitch})')
    ax.set_ylabel('Magnitude')
    ax.set_ylim([0,30])
    ax.set_xlabel('Frequency (Hz)')
    plt.savefig(SAVE_PATH+fname)
    plt.close()

HIST_SCROLL = 500

def plot_energy():
    current_energy = energy_hist[-HIST_SCROLL:]
    time_step = c.T_WIN_LEN/c.F_SAMP
    t = np.arange(max(0, energy_hist.size-HIST_SCROLL)*time_step,
        energy_hist.size*time_step, step=time_step)

    fig, ax = plt.subplots()
    ax.plot(t[:current_energy.size], current_energy, color='g')
    ax.set_title('Weighted Energy')
    ax.set_ylabel('Energy')
    ax.set_ylim([0, 5000])
    ax.set_xlabel('Time (s)')
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

def plot_energy_with_onsets():
    current_energy = energy_hist[-HIST_SCROLL:]
    current_onsets = onset_hist[onset_hist > energy_hist.size-HIST_SCROLL]
    time_step = c.T_WIN_LEN/c.F_SAMP
    t = np.arange(max(0, energy_hist.size-HIST_SCROLL)*time_step,
        energy_hist.size*time_step, step=time_step)
    if energy_hist.size > HIST_SCROLL:
        t_adjust = energy_hist.size - HIST_SCROLL
    else:
        t_adjust = 0

    fig, ax = plt.subplots()
    ax.plot(t[:current_energy.size], current_energy, color='g')
    ax.scatter(t[current_onsets-t_adjust], energy_hist[current_onsets],
        color='r')
    ax.set_title('Weighted Energy')
    ax.set_ylabel('Energy')
    # ax.set_ylim([0, 5000])
    ax.set_xlabel('Time (s)')
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

### Sounddevice Callback and FFTs ###

def sd_callback(indata, frames, time, status):
    global rfft_hist
    if status:
        print(status, file=sys.stderr)
    if any(indata):
        pitch_data = indata[:, 0]
        onset_data = pitch_data.reshape(c.T_WIN_FACTOR, -1)

        pitch_mag = pitch_rfft(pitch_data)
        onset_mags = onset_rffts(onset_data)
        pitch_dq.put(pitch_mag)
        rfft_hist = np.append(rfft_hist, [pitch_mag], axis=0)
        for m in onset_mags:
            onset_dq.put(m)

def pitch_rfft(data):
    return np.abs(fft.rfft(data, n=c.FFT_N))

def onset_rffts(data):
    def rfft_gen(data):
        for d in data:
            yield np.abs(fft.rfft(d, n=c.FFT_N))
    return np.stack([np.array(m) for m in rfft_gen(data)])

## History Updaters ###

def update_hist():
    update_pitch_hist()
    for _ in range(c.T_WIN_FACTOR):
        update_energy_hist()

def update_pitch_hist():
    global pitch_hist, freq_hist, magn_hist
    pitch_data = pitch_dq.get()
    peak_freq, peak_magn = get_peak_freq(pitch_data, c.RFFT_FREQS)
    if not peak_freq:
        pitch = ''
        freq = 0
        magn = 0
    else:
        pitch_freq = find_closest(peak_freq, list(c.FREQS.values()))
        pitch = c.PITCHES[pitch_freq]
        freq = peak_freq
        magn = peak_magn
        # plot_pitch(pitch_data, pitch, freq, magn)

    pitch_hist = np.append(pitch_hist, pitch)
    freq_hist = np.append(freq_hist, freq)
    magn_hist = np.append(magn_hist, magn)

def update_energy_hist():
    global energy_hist
    onset_data = onset_dq.get()
    weights = np.arange(c.RFFT_N)**2
    weighted_energy = (1/c.RFFT_N) * np.sum(weights * onset_data**2)
    energy_hist = np.append(energy_hist, weighted_energy)

def detect_onset():
    global onset_hist
    try:
        start_index = onset_hist[-1]
    except IndexError:
        start_index = 0
    current_hist = energy_hist[start_index:]
    # Full: 5e4
    current_onsets = signal.find_peaks(current_hist, prominence=3e4)[0]
    if current_onsets.size > 1:
        print(f'\tDetected {current_onsets.size} onsets in one window.' \
            'Won\'t be able to resolve pitch.')
    onset_hist = np.append(onset_hist, current_onsets + start_index)

## Other Helpers ###

pitches_printed = 0
def print_pitches():
    global pitches_printed
    if onset_hist.size > pitches_printed and \
        pitch_hist.size > (onset_hist[-1] // c.T_WIN_FACTOR + 3):
        while onset_hist.size > pitches_printed:
            print(pitch_hist[onset_hist[pitches_printed] // c.T_WIN_FACTOR + 3])
            pitches_printed += 1

def save_pitch_resolution():
    try:
        pitch_index = onset_hist[-1] // c.T_WIN_FACTOR
    except:
        return
    if pitch_hist.size > (pitch_index + 10):
        for i in range(pitch_index-5, pitch_index+10):
            splot_pitch(rfft_hist[i], pitch_hist[i], freq_hist[i], magn_hist[i],
                f'pitch_{i}_{i-pitch_index}')
        exit()

def smooth_curve(data):
    N, Wn = signal.buttord(0.1, 0.3, 0.5, 40)
    sos = signal.butter(N, Wn, output='sos')
    return signal.sosfiltfilt(sos, data)

def smooth_energy(energy):
    return energy
    N, Wn = signal.buttord(0.3, 0.4, 0.5, 40)
    sos = signal.butter(N, Wn, output='sos')
    return signal.sosfiltfilt(sos, energy)

def get_peak_freq(magnitude, freqs):
    # magnitude = smooth_curve(magnitude)
    peaks = signal.find_peaks(magnitude, prominence=4, distance=10)[0]
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
