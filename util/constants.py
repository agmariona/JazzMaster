from scipy import fft

N_NGRAM = 5
F_SAMP = 8000 #2700
FFT_N = 1024
RFFT_N = FFT_N//2 + 1
F_WIN_LEN = 280 # 278
T_WIN_FACTOR = 4
T_WIN_LEN = 70
UNIT_DURATION = T_WIN_LEN/F_SAMP # PROB WRONG
FREQS = {'E3'  : 164.81,
         'F3'  : 174.61,
         'F#3' : 185.00,
         'G3'  : 196.00,
         'G#3' : 207.65,
         'A3'  : 220.00,
         'A#3' : 233.08,
         'B3'  : 246.94,
         'C4'  : 261.63,
         'C#4' : 277.18,
         'D4'  : 293.66,
         'D#4' : 311.13,
         'E4'  : 329.63,
         'F4'  : 349.23,
         'F#4' : 369.99,
         'G4'  : 392.00,
         'G#4' : 415.30,
         'A4'  : 440.00,
         'A#4' : 466.16,
         'B4'  : 493.88,
         'C5'  : 523.25,
         'C#5' : 554.37,
         'D5'  : 587.33,
         'D#5' : 622.25,
         'E5'  : 659.25,
         'F5'  : 698.46,
         'F#5' : 739.99,
         'G5'  : 783.99,
         'G#5' : 830.61,
         'A5'  : 880.00,
         'A#5' : 932.33,
         'B5'  : 987.77,
         'C6'  : 1046.50,
         'C#6' : 1108.73,
         'D6'  : 1174.66,
         'D#6' : 1244.51,
         'E6'  : 1318.51}
PITCHES = {v:k for k,v in FREQS.items()}
RFFT_FREQS = fft.rfftfreq(FFT_N, d=1/F_SAMP)
PROJ_PATH = '/Users/agm/Documents/Harvard/ENG-SCI 100/JazzMaster/'
