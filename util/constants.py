from scipy import fft

N_NGRAM = 5
F_SAMP = 8000 #2700
FFT_N = 1024
RFFT_N = FFT_N//2 + 1
F_WIN_LEN = 280 # 278
T_WIN_FACTOR = 4
T_WIN_LEN = 70
TIME_STEP = F_WIN_LEN/(F_SAMP*T_WIN_FACTOR)
PITCH_LOOK_AHEAD = 1
ONSET_PROMINENCE = 1e4
D = 0.025
AGENT_INNER_WINDOW = 0.01
AGENT_OUTER_WINDOW = [-0.02, 0.02]
AGENT_MISS_PENALTY = 8
RHYTHM_TEST_WINDOW = 0.13

PROJ_PATH = '/Users/agm/Documents/Harvard/ENG-SCI 100/JazzMaster/'

RFFT_FREQS = fft.rfftfreq(FFT_N, d=1/F_SAMP)
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

note_to_key = {
    'EN3': '\t',
    'FN3': 'q',
    'F#3': '2',
    'GN3': 'w',
    'G#3': '3',
    'AB3': '3',
    'AN3': 'e',
    'A#3': '4',
    'BB3': '4',
    'BN3': 'r',
    'CN4': 't',
    'C#4': '6',
    'DB4': '6',
    'DN4': 'y',
    'D#4': '7',
    'EB4': '7',
    'EN4': 'u',
    'FN4': 'i',
    'F#4': '9',
    'GB4': '9',
    'GN4': 'o',
    'G#4': '0',
    'AB4': '0',
    'AN4': 'p',
    'A#4': '-',
    'BB4': '-',
    'BN4': '[',
    'CB5': '[',
    'CN5': 'z',
    'C#5': 's',
    'DB5': 's',
    'DN5': 'x',
    'D#5': 'd',
    'EB5': 'd',
    'EN5': 'c',
    'FB5': 'c',
    'FN5': 'v',
    'F#5': 'g',
    'GB5': 'g',
    'GN5': 'b',
    'G#5': 'h',
    'AB5': 'h',
    'AN5': 'n',
    'A#5': 'j',
    'BB5': 'j',
    'BN5': 'm',
    'CN6': ',',
    'C#6': 'l',
    'DN6': '.',
    'D#6': ';',
    'EN6': '/'
}

reference_songs = [
    'take_the_a_train_0.txt',
    'satin_doll_0.txt',
    'moanin_0.txt',
    'all_of_me_0.txt',
    'blue_monk_0.txt',
    'donna_lee_0.txt',
    'for_sentimental_reasons_0.txt',
    'nuages_0.txt',
    'how_deep_is_the_ocean_0.txt',
    'but_not_for_me_0.txt',
    'how_high_the_moon_0.txt',
    'lady_bird_0.txt',
    'jelly_roll_0.txt',
    'nagasaki_0.txt',
    'on_green_dolphin_street_0.txt',
    'quizas_quizas_quizas_0.txt',
    'round_midnight_0.txt',
    'the_girl_from_ipanema_0.txt',
    'waltz_for_debby_0.txt',
    'yardbird_suite_0.txt'
]
