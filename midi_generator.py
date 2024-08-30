import pickle
from mido import Message, MidiFile, MidiTrack
import numpy as np

FILTER_VERBOSE = False

HIGH_NOTE_LIMIT = "C6"
LOW_NOTE_LIMIT = "C2"
PERFORM_LIMIT = True

TICKS_PER_QUARTER_NOTE = 960
THE_SMALLEST_UNIT = TICKS_PER_QUARTER_NOTE

note_to_midi = {
    "C0": 12, "C#0": 13, "Db0": 13, "D0": 14, "D#0": 15, "Eb0": 15, "E0": 16, "F0": 17,
    "F#0": 18, "Gb0": 18, "G0": 19, "G#0": 20, "Ab0": 20, "A0": 21, "A#0": 22, "Bb0": 22,
    "B0": 23, "C1": 24, "C#1": 25, "Db1": 25, "D1": 26, "D#1": 27, "Eb1": 27, "E1": 28,
    "F1": 29, "F#1": 30, "Gb1": 30, "G1": 31, "G#1": 32, "Ab1": 32, "A1": 33, "A#1": 34,
    "Bb1": 34, "B1": 35, "C2": 36, "C#2": 37, "Db2": 37, "D2": 38, "D#2": 39, "Eb2": 39,
    "E2": 40, "F2": 41, "F#2": 42, "Gb2": 42, "G2": 43, "G#2": 44, "Ab2": 44, "A2": 45,
    "A#2": 46, "Bb2": 46, "B2": 47, "C3": 48, "C#3": 49, "Db3": 49, "D3": 50, "D#3": 51,
    "Eb3": 51, "E3": 52, "F3": 53, "F#3": 54, "Gb3": 54, "G3": 55, "G#3": 56, "Ab3": 56,
    "A3": 57, "A#3": 58, "Bb3": 58, "B3": 59, "C4": 60, "C#4": 61, "Db4": 61, "D4": 62,
    "D#4": 63, "Eb4": 63, "E4": 64, "F4": 65, "F#4": 66, "Gb4": 66, "G4": 67, "G#4": 68,
    "Ab4": 68, "A4": 69, "A#4": 70, "Bb4": 70, "B4": 71, "C5": 72, "C#5": 73, "Db5": 73,
    "D5": 74, "D#5": 75, "Eb5": 75, "E5": 76, "F5": 77, "F#5": 78, "Gb5": 78, "G5": 79,
    "G#5": 80, "Ab5": 80, "A5": 81, "A#5": 82, "Bb5": 82, "B5": 83, "C6": 84, "C#6": 85,
    "Db6": 85, "D6": 86, "D#6": 87, "Eb6": 87, "E6": 88, "F6": 89, "F#6": 90, "Gb6": 90,
    "G6": 91, "G#6": 92, "Ab6": 92, "A6": 93, "A#6": 94, "Bb6": 94, "B6": 95, "C7": 96,
    "C#7": 97, "Db7": 97, "D7": 98, "D#7": 99, "Eb7": 99, "E7": 100, "F7": 101, "F#7": 102,
    "Gb7": 102, "G7": 103, "G#7": 104, "Ab7": 104, "A7": 105, "A#7": 106, "Bb7": 106, "B7": 107,
    "C8": 108, "C#8": 109, "Db8": 109, "D8": 110, "D#8": 111, "Eb8": 111, "E8": 112, "F8": 113,
    "F#8": 114, "Gb8": 114, "G8": 115, "G#8": 116, "Ab8": 116, "A8": 117, "A#8": 118, "Bb8": 118,
    "B8": 119, "C9": 120, "C#9": 121, "Db9": 121, "D9": 122, "D#9": 123, "Eb9": 123, "E9": 124,
    "F9": 125, "F#9": 126, "Gb9": 126, "G9": 127
}

moll_tons = {
    "C-moll": ["C", "D", "D#", "F", "G", "G#", "A#"],
    "C#-moll": ["C#", "D#", "E", "F#", "G#", "A", "B"],
    "D-moll": ["D", "E", "F", "G", "A", "A#", "C"],
    "D#-moll": ["D#", "F", "F#", "G#", "A#", "B", "C#"],
    "E-moll": ["E", "F#", "G", "A", "B", "C", "D"],
    "F-moll": ["F", "G", "G#", "A#", "C", "C#", "D#"],
    "F#-moll": ["F#", "G#", "A", "B", "C#", "D", "E"],
    "G-moll": ["G", "A", "A#", "C", "D", "D#", "F"],
    "G#-moll": ["G#", "A#", "B", "C#", "D#", "E", "F#"],
    "A-moll": ["A", "B", "C", "D", "E", "F", "G"],
    "A#-moll": ["A#", "C", "C#", "D#", "F", "F#", "G#"],
    "H-moll": ["H", "C#", "D", "E", "F#", "G", "A"]
}

tons_sounds_counters = {
    "C-moll": 0.0,
    "C#-moll": 0.0,
    "D-moll": 0.0,
    "D#-moll": 0.0,
    "E-moll": 0.0,
    "F-moll": 0.0,
    "F#-moll": 0.0,
    "G-moll": 0.0,
    "G#-moll": 0.0,
    "A-moll": 0.0,
    "A#-moll": 0.0,
    "H-moll": 0.0
}


def is_note_stable(note_name, counter, notes_names_table, ticks_per_frame, the_smallest_unit):
    expected_range = int(np.ceil(the_smallest_unit / ticks_per_frame))
    if len(notes_names_table) - counter < expected_range:
        return True

    for index in range(expected_range):
        if note_name not in notes_names_table[counter + index]:
            return False
    return True


def is_dominating_note(note, second_note, counter, notes_names_table):
    while counter < len(notes_names_table) - 1:
        if note not in notes_names_table[counter] and second_note in notes_names_table[counter]:
            return False
        elif note in notes_names_table[counter] and second_note not in notes_names_table[counter]:
            return True
        counter += 1


def are_note_properties_ok(note_name, counter, notes_name_table, active_notes, tone, ticks_per_frame, the_smallest_unit):
    if tone != "" and note_name[:-1] not in moll_tons[tone]:
        return False

    if PERFORM_LIMIT and (note_to_midi[note_name] >= note_to_midi[HIGH_NOTE_LIMIT] or note_to_midi[note_name] < note_to_midi[LOW_NOTE_LIMIT]):
        return False

    if not is_note_stable(note_name, counter, notes_name_table, ticks_per_frame, the_smallest_unit):
        return False

    for second_note in active_notes:
        if active_notes[second_note] and second_note != note_name \
                and (note_to_midi[note_name] == note_to_midi[second_note] - 1 or note_to_midi[note_name] == note_to_midi[second_note] + 1):
            if FILTER_VERBOSE:
                print(f"Comparing {note_name}, {second_note}")
            if not is_dominating_note(note_name, second_note, counter, notes_name_table):
                if FILTER_VERBOSE:
                    print(f"{second_note} won")
                return False

    max_range = min(8, len(notes_name_table) - 1 - counter)
    for second_counter in range(counter, counter + max_range):
        for second_note in notes_name_table[second_counter]:
            if second_note != note_name \
                    and (note_to_midi[note_name] == note_to_midi[second_note] - 1 or note_to_midi[note_name] == note_to_midi[second_note] + 1):
                if FILTER_VERBOSE:
                    print(f"Comparing {note_name}, {second_note}")
                if not is_dominating_note(note_name, second_note, second_counter, notes_name_table):
                    if FILTER_VERBOSE:
                        print(f"{second_note} won")
                    return False
    if FILTER_VERBOSE:
        print(f"{note_name} survived")
    return True


def is_note_lost(note, current_notes, future_notes):
    if note not in current_notes and note in future_notes:
        return True
    return False


def stabilize_notes(big_notes_result):
    preprocessed_notes = big_notes_result.copy()
    for index, notes in enumerate(big_notes_result):
        if FILTER_VERBOSE:
            print(f"NOTES: {notes}")
        previous_notes = []
        current_notes = []
        future_notes = []

        for note in notes:
            current_notes.append(note[1])

        if index != 0:
            for note in preprocessed_notes[index - 1]:
                previous_notes.append(note)

        if index != len(preprocessed_notes) - 1:
            for note in preprocessed_notes[index + 1]:
                future_notes.append(note[1])

        if not previous_notes or not future_notes:
            continue

        for note in previous_notes:
            if is_note_lost(note[1], current_notes, future_notes):
                preprocessed_notes[index].append(note)

    return preprocessed_notes


def find_tone(notes_names_table):
    moll_tons_counters = {}
    for notes in notes_names_table:
        for note in notes:
            for ton in moll_tons:
                if note[:-1] in moll_tons[ton]:
                    if ton not in moll_tons_counters:
                        moll_tons_counters[ton] = 1
                    else:
                        moll_tons_counters[ton] += 1
    print(moll_tons_counters)
    found_ton = max(moll_tons_counters, key=moll_tons_counters.get)
    return found_ton


def generate(input_name, bpm, fps, precision, deduce_tone, tone):
    the_smallest_unit = THE_SMALLEST_UNIT
    ticks_per_frame = int((TICKS_PER_QUARTER_NOTE * bpm) / (60 * fps))

    if precision == 2:
        the_smallest_unit = int(the_smallest_unit / 2)
    elif precision == 3:
        the_smallest_unit = int(the_smallest_unit / 4)
    elif precision == 4:
        the_smallest_unit = int(the_smallest_unit / 8)

    print(f'Frame length: {ticks_per_frame}, ticks per minimal note: {the_smallest_unit}')

    with open(input_name + ".pickle", 'rb') as file:
        big_notes_result = pickle.load(file)

    mid = MidiFile(type=0)
    mid.ticks_per_beat = TICKS_PER_QUARTER_NOTE
    track0 = MidiTrack()

    notes_names_table = []
    notes_volumes_progress_table = []

    big_notes_result = stabilize_notes(big_notes_result)

    for notes in big_notes_result:
        current_notes = []
        current_volumes = []
        for note in notes:
            if note[1] in note_to_midi and note[1] not in current_notes:
                current_notes.append(note[1])
                current_volumes.append([note[1], note[2]])
        notes_names_table.append(current_notes)
        notes_volumes_progress_table.append(current_volumes)

    global_max_volume = 0.0
    for notes_volumes in notes_volumes_progress_table:
        for note in notes_volumes:
            if note[1] > global_max_volume:
                global_max_volume = note[1]

    notes_volumes_table = []

    for index, notes_volumes in enumerate(notes_volumes_progress_table):
        frame_notes = []
        for note in notes_volumes:
            note_max_volume = note[1]
            for frame_index in range(index, len(notes_volumes_progress_table)):
                note_found = False
                for frame_note in notes_volumes_progress_table[frame_index]:
                    if frame_note[0] == note[0]:
                        if frame_note[1] > note_max_volume:
                            note_max_volume = frame_note[1]
                        note_found = True
                if not note_found:
                    break
            frame_notes.append([note[0], note_max_volume])
        notes_volumes_table.append(frame_notes)

    if tone == "":
        if deduce_tone:
            tone = find_tone(notes_names_table)
            print(f"Tone not given as argument. Found tone: {tone}")
        else:
            print(f"Tone not given as argument. Deducing OFF")

    current_notes = []
    previous_notes = []
    current_time = 0
    last_message_time = 0

    active_notes = {}

    for counter, notes in enumerate(notes_names_table):
        last_smallest_unit = int(current_time // the_smallest_unit) * the_smallest_unit
        if FILTER_VERBOSE:
            print(f"{notes}", end="\t")
        for note_number, note in enumerate(notes):
            if note not in previous_notes:
                if are_note_properties_ok(note, counter, notes_names_table, active_notes, tone, ticks_per_frame, the_smallest_unit):
                    volume = int((notes_volumes_table[counter][note_number][1] / global_max_volume) * 127 / 2) + 63
                    track0.append(Message('note_on',
                                          note=int(note_to_midi[note]),
                                          velocity=volume,
                                          time=last_smallest_unit - last_message_time))
                    if FILTER_VERBOSE:
                        print(f'Note {note} activated from frame No. {counter}, {current_time} at time {last_smallest_unit}')
                    current_notes.append(note)
                    active_notes[note] = True
                    last_message_time = last_smallest_unit
            else:
                current_notes.append(note)

        for note in previous_notes:
            if note not in current_notes:
                track0.append(Message('note_off',
                                      note=int(note_to_midi[note]),
                                      velocity=0,
                                      time=last_smallest_unit - last_message_time))
                if FILTER_VERBOSE:
                    print(f'Note {note} deactivated from frame No. {counter}, {current_time}, at time {last_smallest_unit}')
                if active_notes[note]:
                    active_notes[note] = False
                last_message_time = last_smallest_unit
        if FILTER_VERBOSE:
            print("\n")
        previous_notes = current_notes.copy()
        current_notes.clear()
        current_time += ticks_per_frame

    mid.tracks.append(track0)

    output_name = input_name + " - result.mid"

    mid.save(output_name)
