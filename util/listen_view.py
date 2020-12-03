import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from scipy.fft import rfft, rfftfreq
import sys

from listen import *

energy_history = np.load('data/energy2.npy', allow_pickle=True)
pitch_history = np.load('data/pitch2.npy', allow_pickle=True)
data_history = np.load('data/data2.npy', allow_pickle=True)
onsets = np.load('data/onsets2.npy', allow_pickle=True)
onsets = np.insert(onsets, 0, 0)
onsets = onsets

print(pitch_history)
print(onsets)
print(pitch_history[onsets+3])
plot_onsets(energy_history, onsets)
for i in range(onsets[1]+3-8, onsets[1]+3):
    display_magnitude(data_history[i], FFT_FREQS, pitch_history[i+1])
