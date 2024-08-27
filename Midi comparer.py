import mido

approximation_limit = 240 # 16-note

midi_to_note = {
    12: ["C0"],
    13: ["C#0", "Db0"],
    14: ["D0"],
    15: ["D#0", "Eb0"],
    16: ["E0"],
    17: ["F0"],
    18: ["F#0", "Gb0"],
    19: ["G0"],
    20: ["G#0", "Ab0"],
    21: ["A0"],
    22: ["A#0", "Bb0"],
    23: ["B0"],
    24: ["C1"],
    25: ["C#1", "Db1"],
    26: ["D1"],
    27: ["D#1", "Eb1"],
    28: ["E1"],
    29: ["F1"],
    30: ["F#1", "Gb1"],
    31: ["G1"],
    32: ["G#1", "Ab1"],
    33: ["A1"],
    34: ["A#1", "Bb1"],
    35: ["B1"],
    36: ["C2"],
    37: ["C#2", "Db2"],
    38: ["D2"],
    39: ["D#2", "Eb2"],
    40: ["E2"],
    41: ["F2"],
    42: ["F#2", "Gb2"],
    43: ["G2"],
    44: ["G#2", "Ab2"],
    45: ["A2"],
    46: ["A#2", "Bb2"],
    47: ["B2"],
    48: ["C3"],
    49: ["C#3", "Db3"],
    50: ["D3"],
    51: ["D#3", "Eb3"],
    52: ["E3"],
    53: ["F3"],
    54: ["F#3", "Gb3"],
    55: ["G3"],
    56: ["G#3", "Ab3"],
    57: ["A3"],
    58: ["A#3", "Bb3"],
    59: ["B3"],
    60: ["C4"],
    61: ["C#4", "Db4"],
    62: ["D4"],
    63: ["D#4", "Eb4"],
    64: ["E4"],
    65: ["F4"],
    66: ["F#4", "Gb4"],
    67: ["G4"],
    68: ["G#4", "Ab4"],
    69: ["A4"],
    70: ["A#4", "Bb4"],
    71: ["B4"],
    72: ["C5"],
    73: ["C#5", "Db5"],
    74: ["D5"],
    75: ["D#5", "Eb5"],
    76: ["E5"],
    77: ["F5"],
    78: ["F#5", "Gb5"],
    79: ["G5"],
    80: ["G#5", "Ab5"],
    81: ["A5"],
    82: ["A#5", "Bb5"],
    83: ["B5"],
    84: ["C6"],
    85: ["C#6", "Db6"],
    86: ["D6"],
    87: ["D#6", "Eb6"],
    88: ["E6"],
    89: ["F6"],
    90: ["F#6", "Gb6"],
    91: ["G6"],
    92: ["G#6", "Ab6"],
    93: ["A6"],
    94: ["A#6", "Bb6"],
    95: ["B6"],
    96: ["C7"],
    97: ["C#7", "Db7"],
    98: ["D7"],
    99: ["D#7", "Eb7"],
    100: ["E7"],
    101: ["F7"],
    102: ["F#7", "Gb7"],
    103: ["G7"],
    104: ["G#7", "Ab7"],
    105: ["A7"],
    106: ["A#7", "Bb7"],
    107: ["B7"],
    108: ["C8"],
    109: ["C#8", "Db8"],
    110: ["D8"],
    111: ["D#8", "Eb8"],
    112: ["E8"],
    113: ["F8"],
    114: ["F#8", "Gb8"],
    115: ["G8"],
    116: ["G#8", "Ab8"],
    117: ["A8"],
    118: ["A#8", "Bb8"],
    119: ["B8"],
    120: ["C9"],
    121: ["C#9", "Db9"],
    122: ["D9"],
    123: ["D#9", "Eb9"],
    124: ["E9"],
    125: ["F9"],
    126: ["F#9", "Gb9"],
    127: ["G9"]
}


def read_midi_notes(file_path):
    midi = mido.MidiFile(file_path)
    notes = []

    for track in midi.tracks:
        current_time = 0
        for msg in track:
            print(msg)
            # if msg.type == "note_on" or msg.type == "note_off":
            #     print(f"Type: {msg.type}, note: {msg.note}, time: {msg.time}")
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:  # Note on event
                notes.append((current_time, msg.note))
                # print(current_time, end=", ")

    print("\n")
    return notes


def compare_midi_files(file1, file2):
    print("Original:")
    notes1 = read_midi_notes(file1)
    print("\nReproduction:")
    notes2 = read_midi_notes(file2)

    matched_notes = 0
    almost_matched_notes = 0

    # Use a set for fast lookup
    notes2_set = set(notes2)
    matched_notes_set = set()
    almost_matched_notes_set = set()

    for note in notes1:
        if note in notes2_set:
            matched_notes += 1
            matched_notes_set.add(note)
        for shift in range(note[0] - approximation_limit, note[0] + approximation_limit):
            shifted_time = note[0] + shift
            shifted_note = (shifted_time, note[1])
            if shifted_note in notes2_set:
                almost_matched_notes += 1
                almost_matched_notes_set.add(note)

    total_notes = len(notes1)
    percentage_match = (matched_notes / total_notes) * 100 if total_notes > 0 else 0
    percentage_almost_match = (almost_matched_notes / total_notes) * 100 if total_notes > 0 else 0

    return matched_notes, percentage_match, matched_notes_set, almost_matched_notes, percentage_almost_match, almost_matched_notes_set


# Przykład użycia
file1 = 'dramatic piano - how should it be.mid'
file2 = 'Sample 1 - source - result.mid'

matched_notes_count, percentage_match, matched_notes_set, almost_matched_count, percentage_almost_match, almost_matched_notes_set = compare_midi_files(file1, file2)

for note in matched_notes_set:
    print(f"Matched note: {note[0], midi_to_note[note[1]]}")
print(f"Number of matched notes: {matched_notes_count}")
print(f"Accuracy : {percentage_match:.2f}%")

# for note in almost_matched_notes_set:
#     print(f"Matched note: {note[0], midi_to_note[note[1]]}")
# print(f"Number of matched notes: {almost_matched_count}")
# print(f"Accuracy : {percentage_almost_match:.2f}%")
