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
    'major-sixth': '6',
    'diminished-seventh': 'dim6',
    'minor-sixth': 'm6',
    'augmented': 'aug',
    'major-seventh': 'maj7',
    'diminished': 'dim',
    'major-minor': 'mM7',
    None: '',
    'dominant-13th': '13',
    'minor-ninth': 'm9',
    'major-ninth': 'maj9',
    'dominant-11th': '11',
    'dominant-seventh': '7',
    'maj69': '69',
    'minor-11th': 'm9',
    'augmented-ninth': '9#5',
    'suspended-second': 'sus2',
    'minor-major': 'mM7',
    'min': 'm',
    ' ': '',
    '7': '7',
    'maj7': 'maj7',
    'sus47': '7sus4',
    'major-13th': 'maj9',
    'power': '5',
    'other': 'dim'
}

def parse_xml(path):
    fname = path.split('/')[-1].split('.')[0]+'.txt'
    # print(f'Processing {fname}.')

    xml_tree = xml.etree.ElementTree.parse(path)
    parts = xml_tree.getroot().findall('part')
    if len(parts) > 1:
        return -1
    elif len(parts) == 0:
        print('Error: No part found.')
        exit(1)
    measures = parts[0].findall('measure')

    divisions = int(measures[0].find('attributes/divisions').text)

    notes = list()
    durations = list()
    chords = list()

    i = 0
    repeat_start = 0
    repeated = False
    repeat_count = 1
    current_chord = None
    current_ending = None
    tied_note = None
    tied_duration = 0
    tied_chord = None

    while i < len(measures):
        next_i = i + 1

        note_buf = list()
        duration_buf = list()
        chord_buf = list()

        ending_failsafe_break = False

        for child in measures[i]:
            if child.tag == 'barline':
                if child.find('ending') is not None and child.find('ending').attrib['type'] != 'discontinue':
                    try:
                        current_ending = int(child.find('ending').attrib['number'])
                        if repeat_count > current_ending:
                            break
                        else:
                            ending_failsafe_break = False
                    except ValueError:
                        try:
                            if child.find('ending').attrib['number'][1] == '.':
                                ending_numbers = [int(n) for n in
                                    child.find('ending').attrib['number'].split('.') if n]
                            else:
                                ending_numbers = [int(n) for n in
                                    child.find('ending').attrib['number'].split(', ')]

                            if repeat_count > max(ending_numbers):
                                break
                            else:
                                repeated = False
                                current_ending = repeat_count + 1
                                ending_failsafe_break = False
                        except:
                            return -2

                if child.find('repeat') is not None:
                    direction = child.find('repeat').attrib['direction']
                    if direction == 'forward':
                        if not repeated:
                            repeat_start = i
                    elif direction == 'backward':
                        if not repeated:
                            next_i = repeat_start
                            repeated = True
                            repeat_count += 1
                            current_ending = None
                        elif child.find('ending') is None:
                            break
                    else:
                        print('Error: Unknown repeat direction.')
                        exit(1)

            elif current_ending and repeat_count != current_ending:
                ending_failsafe_break = True

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
                    try:
                        note = pitch_note + pitch_alter + pitch_octave
                    except:
                        return -3

                elif child.find('rest') is not None:
                    note = 'RNO'

                else:
                    print('Error: Note is not a rest but has no pitch.')
                    exit(1)

                try:
                    duration = int(child.find('duration').text)
                except AttributeError:
                    return -4

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
            if not ending_failsafe_break:
                # print(f'Reading measure {i+1}')
                notes += note_buf
                durations += duration_buf
                chords += chord_buf

        i = next_i

    assert len(notes) == len(durations) == len(chords)

    txt_path = constants.PROJ_PATH + f'library/txt/{fname}'
    with open(txt_path, 'w') as f:
        for i in range(len(notes)):
            f.write(f'{notes[i]} {durations[i]} {chords[i]}\n')
