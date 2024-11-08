from music21 import converter
from music21 import stream, note, interval
import numpy as np
import os
from music21 import note, interval
#the following functions are used to calculate the intervals between notes in a piece of music

def simplify_interval(interval):
    s = interval
    letter = ''.join(filter(str.isalpha, s))
    number = ''.join(filter(str.isdigit, s))
    number = int(number)

    if(number > 8):
        number = 15 - number

    number = str(number)

    final_interval = letter + number
    return final_interval

def calculate_interval(note1, note2):
    n1 = note.Note(note1)
    n2 = note.Note(note2)
    
    intvl = interval.Interval(noteStart=n1, noteEnd=n2)
    return intvl.name

def calculate_intervals(part_measures, tonic):
    intervals = []
    prev_notes = []
    for measure in part_measures:
        if isinstance(measure, stream.base.Measure):
            prev_note = None
            for element in measure.notesAndRests:
                if element.isNote:
                    if prev_note is not None:
                        final_interval = simplify_interval(calculate_interval(tonic, element.pitch))
                        prev_notes.append(final_interval)
                        interval = calculate_interval(prev_note.pitch, element.pitch)
                        interval = simplify_interval(interval)
                        intervals.append(interval)
                    prev_note = element
    return intervals, prev_notes


def get_notes(all_intervals, all_prev_notes, folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            score = converter.parse(file_path)
        except:
            print('Error parsing file: ', file_path)
            continue
        key_sig = score.analyze('key')
        tonic = key_sig.tonic

        part_measures = score.parts[0].measures(numberStart=1, numberEnd=None)
        intervals, prev_notes = calculate_intervals(part_measures, tonic)
        all_intervals.extend(intervals)
        all_prev_notes.extend(prev_notes)





#the following functions are used to generate a note chain
def calculate_note(n, interval):
    n1 = note.Note(n)
    n2 = note.Note()
    n2.pitch = n1.pitch.transpose(interval)
    return n2.name

def simulate_MC(current_position, prob_matrix, row_names):
    row = row_names.index(current_position)
    probs = prob_matrix.iloc[row, :]
    return np.random.choice(probs.index, p=probs.values)

def conversions(tonic, prob_matrix, n, row_names):
    note_chain = []
    note_position_chain = []

    note_chain.append(tonic)
    note_position_chain.append('P1')

    current_note = tonic
    currernt_position = 'P1'

    while n > 0:
        new_interval = simulate_MC(currernt_position, prob_matrix, row_names)
        current_note = calculate_note(current_note, new_interval)
        current_position = calculate_interval(tonic, current_note)

        note_chain.append(current_note)
        note_position_chain.append(current_position)
        n -= 1

    return note_chain


#The following functions are used to create the rhythm transition matrix

def extract_rhythm(part_measures):
    rhythm = []
    prev_rhythm = []
    prev_note = 0
    for measure in part_measures:
        if isinstance(measure, stream.base.Measure):
            for element in measure.notesAndRests:
                if isinstance(element, note.Note) or isinstance(element, note.Rest):
                    prev_rhythm.append(element.duration.quarterLength)
                    rhythm.append(prev_note)
                    prev_note = element.duration.quarterLength
    return rhythm, prev_rhythm

def get_rhythms(all_rhythm, all_prev_rhythm, folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            score = converter.parse(file_path)
        except:
            continue
        part_measures = score.parts[0].measures(numberStart=1, numberEnd=None)
        rhythm, prev_rhythm = extract_rhythm(part_measures)
        all_rhythm.extend(rhythm)
        all_prev_rhythm.extend(prev_rhythm)

def simulate_MC2(current_position, prob_matrix, row_names, n):
    rhythms = []
    while n > 0:
        row = row_names.index(current_position)
        probs = prob_matrix.iloc[row, :]
        n -= 1
        new_rhythm = np.random.choice(probs.index, p=probs.values)
        rhythms.append(new_rhythm)
        current_position = new_rhythm
    return rhythms