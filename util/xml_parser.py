import argparse
from fractions import Fraction
import xml.etree.ElementTree
import constants

kind_to_quality = {
    'major': '',
    'minor': 'm',
    'dominant': '7',
    'augmented-seventh': '7#5',
    'half-diminished': 'm7b5',
    'minor-seventh': 'm7',
    'suspended-fourth': 'sus4',
    'dominant-ninth': '9',
    'major-sixth': '6'
}

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('xml', type=str, help='path to .xml to parse')
parser.add_argument('-c', action='store_true', help='play chords')
args = parser.parse_args()

assert args.xml.split('/')[-1].split('.')[-1] == 'xml'

xml_tree = xml.etree.ElementTree.parse(args.xml)
parts = xml_tree.getroot().findall('part')
if len(parts) > 1:
    print('Error: Too many parts. Not sure how to distinguish.')
    exit(1)
elif len(parts) == 0:
    print('Error: No part found.')
    exit(1)
measures = parts[0].findall('measure')

divisions = int(measures[0].find('attributes/divisions').text)

notes = list()
durations = list()
chords = list()

i = 0
repeat_start = -1
repeated = False
current_chord = None
current_ending = None
tied_note = None
tied_duration = 0
tied_chord = None

while i < len(measures):
    # print(f'Measure {i+1}')
    next_i = i + 1

    note_buf = list()
    duration_buf = list()
    chord_buf = list()

    for child in measures[i]:
        if child.tag == 'barline':
            if child.find('ending') is not None:
                assert current_ending
                ending_number = int(child.find('ending').attrib['number'])
                # print(f'\tWorking with ending {ending_number}')
                if current_ending > ending_number:
                    break
                elif child.find('ending').attrib['type'] == 'discontinue':
                    current_ending = None

            if child.find('repeat') is not None:
                direction = child.find('repeat').attrib['direction']
                if direction == 'forward':
                    if not repeated:
                        repeat_start = i
                        current_ending = 1
                    if repeated:
                        current_ending += 1
                    # print(f'\tRepeating with ending {current_ending}')
                elif direction == 'backward':
                    if not repeated:
                        next_i = repeat_start
                        repeated = True
                    elif child.find('ending') is None:
                        break
                else:
                    print('Error: Unknown repeat direction.')
                    exit(1)

        if child.tag == 'harmony':
            root_step = child.find('root/root-step').text
            root_alter = child.find('root/root-alter')
            if root_alter is None:
                root_alter = ''
            elif root_alter.text == '-1':
                root_alter = 'b'
            elif root_alter.text == '1':
                root_alter = '#'
            kind = child.find('kind').text
            try:
                quality = kind_to_quality[kind]
            except KeyError:
                print(f'Error: Unknown chord type {kind} in measure {i+1}')
                exit(1)
            current_chord = root_step+root_alter+quality

        elif child.tag == 'note':
            if child.find('pitch'):
                pitch_note = child.find('pitch/step').text
                pitch_alter = child.find('pitch/alter')
                if pitch_alter is None:
                    pitch_alter = 'N'
                elif pitch_alter.text == '-1':
                    pitch_alter = 'B'
                elif pitch_alter.text == '1':
                    pitch_alter = '#'
                pitch_octave = child.find('pitch/octave').text
                note = pitch_note + pitch_alter + pitch_octave

            elif child.find('rest') is not None:
                note = 'RNO'

            else:
                print('Error: Note is not a rest but has no pitch.')
                exit(1)

            duration = int(child.find('duration').text)

            tie_start = False
            tie_stop = False
            for tie in child.findall('tie'):
                if tie.attrib['type'] == 'start':
                    tie_start = True
                elif tie.attrib['type'] == 'stop':
                    tie_stop = True

            if tie_start:
                # print(f'\nNote: {note}. Chord: {current_chord}')
                # print('Has tie.')
                if tied_note:
                    if tied_chord != current_chord:
                        # print('Tied chord doesn\'t match current chord.')
                        note_buf.append(tied_note)
                        tied_duration = str(Fraction(tied_duration, divisions))
                        duration_buf.append(tied_duration)
                        chord_buf.append(tied_chord)
                        tied_note = note
                        tied_duration = duration
                        tied_chord = current_chord
                        continue
                    else:
                        # print('Tied chord matches current chord.')
                        tied_duration += duration
                        continue
                else:
                    # print(f'Starting tie in measure {i+1}.')
                    current_tied = True
                    tied_note = note
                    tied_duration = duration
                    tied_chord = current_chord
                    continue
            elif tie_stop or tied_note:
                assert not tie_start
                # print(f'\nNote: {note}. Chord: {current_chord}')
                # print(f'Ending tie in measure {i+1}.')
                if tied_chord != current_chord:
                    # print('\tDoesn\'t match chord')
                    note_buf.append(tied_note)
                    tied_duration = str(Fraction(tied_duration, divisions))
                    duration_buf.append(tied_duration)
                    chord_buf.append(tied_chord)
                else:
                    # print('\tMatches chord.')
                    duration += tied_duration
                tied_note = None
                tied_duration = 0
                tied_chord = None

            duration = str(Fraction(duration, divisions))

            note_buf.append(note)
            duration_buf.append(duration)
            chord_buf.append(current_chord)
    else:
        print(f'Reading measure {i+1}')
        notes += note_buf
        durations += duration_buf
        chords += chord_buf

    i = next_i

assert len(notes) == len(durations) == len(chords)

fname = args.xml.split('/')[-1].split('.')[0]+'.txt'
print(f'Writing {fname}.')
txt_path = constants.PROJ_PATH + f'library/txt/{fname}'

with open(txt_path, 'w') as f:
    for i in range(len(notes)):
        f.write(f'{notes[i]} {durations[i]} {chords[i]}\n')
