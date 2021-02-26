from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import queue
from scipy import fft, signal

import util.constants as c
import util.util as util

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

def plot_pitch(rfft, pitch, freq, magn, fname=None):
    fig, ax = plt.subplots()
    ax.plot(c.RFFT_FREQS/1000, rfft, color='b')
    if magn > 0:
        ax.scatter(freq/1000, magn, color='r')
    ax.set_title(f'Single-Sided DFT of Audio Input')
    ax.set_ylabel('Magnitude')
    ax.set_ylim([0,50])
    ax.set_xlabel('Frequency (kHz)')

    plt.tight_layout()
    if fname:
        plt.savefig(SAVE_PATH+fname, dpi=300)
    else:
        plt.show(block=False)
        plt.pause(0.1)
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

    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

def plot_energy_with_onsets(fname=None):
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
    ax.plot(t[:current_energy.size], current_energy/1000, color='g')
    ax.scatter(t[current_onsets-t_adjust], energy_hist[current_onsets]/1000,
        color='r')
    ax.set_title('Weighted Energy of Audio Input')
    ax.set_ylabel('Energy (Arbitrary Units)')
    ax.set_xlabel('Time (s)')

    plt.tight_layout()
    if fname:
        plt.savefig(SAVE_PATH+fname, dpi=300)
    else:
        plt.show(block=False)
        plt.pause(0.01)
    plt.close()

### Plot Drivers ###

def save_pitch_resolution():
    try:
        pitch_index = onset_hist[-1] // c.T_WIN_FACTOR
    except:
        return
    if pitch_hist.size > (pitch_index + 10):
        for i in range(pitch_index-5, pitch_index+10):
            plot_pitch(rfft_hist[i], pitch_hist[i], freq_hist[i], magn_hist[i],
                fname=f'pitch_{i:03}_{i-pitch_index}')
        exit()

def save_onsets(n_onsets):
    if onset_hist.size < n_onsets:
        return
    earliest_onset = onset_hist[-n_onsets]
    time_step = c.T_WIN_LEN/c.F_SAMP
    if energy_hist.size > HIST_SCROLL:
        t_adjust = energy_hist.size - HIST_SCROLL
    else:
        t_adjust = 0
    t = np.arange(max(0, energy_hist.size-HIST_SCROLL)*time_step,
        energy_hist.size*time_step, step=time_step)
    if earliest_onset-t_adjust > 100:
        return
    plot_energy_with_onsets(fname='energy_with_onsets')
    exit()

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

def detect_onset(prominence):
    global onset_hist
    try:
        start_index = onset_hist[-1]
    except IndexError:
        start_index = 0
    current_hist = energy_hist[start_index:]
    # Full: 5e4
    current_onsets = signal.find_peaks(current_hist, prominence=prominence)[0]
    if current_onsets.size > 1:
        print(f'\tDetected {current_onsets.size} onsets in one window.' \
            'Won\'t be able to resolve pitch.')
    onset_hist = np.append(onset_hist, current_onsets + start_index)

events_loaded = 0
def load_buffer(logging):
    buf = []
    global events_loaded
    if onset_hist.size > events_loaded and \
        pitch_hist.size > \
        (onset_hist[-1] // c.T_WIN_FACTOR + c.PITCH_LOOK_AHEAD):
        while onset_hist.size > (events_loaded+1):
            pitch = ''
            j = 0
            while pitch == '':
                pitch = pitch_hist[onset_hist[events_loaded] //
                    c.T_WIN_FACTOR + c.PITCH_LOOK_AHEAD + j]
            if logging:
                print(f'NOTE {pitch} {datetime.now().time()}')
            pitch = util.note_to_midi(pitch)
            start = round(onset_hist[events_loaded] * c.TIME_STEP, ndigits=3)
            stop = round(onset_hist[events_loaded+1] * c.TIME_STEP, ndigits=3)
            buf.append((pitch, start, stop))
            events_loaded += 1
    return buf


### Printers ###

pitches_printed = 0
def print_pitches():
    global pitches_printed
    if onset_hist.size > pitches_printed and \
        pitch_hist.size > (onset_hist[-1] // c.T_WIN_FACTOR + 3):
        while onset_hist.size > pitches_printed:
            print(
                pitch_hist[onset_hist[pitches_printed] // c.T_WIN_FACTOR + 3])
            pitches_printed += 1


## Other Helpers ###

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
