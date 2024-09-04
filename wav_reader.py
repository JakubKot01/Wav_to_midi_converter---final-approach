import numpy as np
from scipy.io import wavfile
import tqdm
import pickle
import bisect

# Słownik mapujący częstotliwości na nuty
freq_to_note = {
    16.35: "C0", 17.32: "C#0", 18.35: "D0", 19.45: "D#0", 20.60: "E0", 21.83: "F0", 23.12: "F#0", 24.50: "G0", 25.96: "G#0", 27.50: "A0", 29.14: "A#0", 30.87: "B0",
    32.70: "C1", 34.65: "C#1", 36.71: "D1", 38.89: "D#1", 41.20: "E1", 43.65: "F1", 46.25: "F#1", 49.00: "G1", 51.91: "G#1", 55.00: "A1", 58.27: "A#1", 61.74: "B1",
    65.41: "C2", 69.30: "C#2", 73.42: "D2", 77.78: "D#2", 82.41: "E2", 87.31: "F2", 92.50: "F#2", 98.00: "G2", 103.83: "G#2", 110.00: "A2", 116.54: "A#2", 123.47: "B2",
    130.81: "C3", 138.59: "C#3", 146.83: "D3", 155.56: "D#3", 164.81: "E3", 174.61: "F3", 185.00: "F#3", 196.00: "G3", 207.65: "G#3", 220.00: "A3", 233.08: "A#3", 246.94: "B3",
    261.63: "C4", 277.18: "C#4", 293.66: "D4", 311.13: "D#4", 329.63: "E4", 349.23: "F4", 369.99: "F#4", 392.00: "G4", 415.30: "G#4", 440.00: "A4", 466.16: "A#4", 493.88: "B4",
    523.25: "C5", 554.37: "C#5", 587.33: "D5", 622.25: "D#5", 659.25: "E5", 698.46: "F5", 739.99: "F#5", 783.99: "G5", 830.61: "G#5", 880.00: "A5", 932.33: "A#5", 987.77: "B5",
    1046.50: "C6", 1108.73: "C#6", 1174.66: "D6", 1244.51: "D#6", 1318.51: "E6", 1396.91: "F6", 1479.98: "F#6", 1567.98: "G6", 1661.22: "G#6", 1760.00: "A6", 1864.66: "A#6", 1975.53: "B6",
    2093.00: "C7", 2217.46: "C#7", 2349.32: "D7", 2489.02: "D#7", 2637.02: "E7", 2793.83: "F7", 2959.96: "F#7", 3135.96: "G7", 3322.44: "G#7", 3520.00: "A7", 3729.31: "A#7", 3951.07: "B7",
    4186.01: "C8", 4434.92: "C#8", 4698.63: "D8", 4978.03: "D#8", 5274.04: "E8", 5587.65: "F8", 5919.91: "F#8", 6271.93: "G8", 6644.88: "G#8", 7040.00: "A8", 7458.62: "A#8", 7902.13: "B8"
}

# Zamieniamy klucze słownika na posortowaną listę
frequencies = sorted(freq_to_note.keys())

def find_closest_frequency(freq):
    # Znajdź indeks najbliższej częstotliwości w posortowanej liście
    idx = bisect.bisect_left(frequencies, freq)
    if idx == 0:
        return frequencies[0]
    if idx == len(frequencies):
        return frequencies[-1]
    before = frequencies[idx - 1]
    after = frequencies[idx]
    # Wybierz najbliższą częstotliwość
    if after - freq < freq - before:
        return after
    else:
        return before

FFT_WINDOW_SECONDS = [0.05, 0.2, 0.3, 0.4, 0.6]

def extract_sample(audio, frame_number, fft_window_size, frame_offset):
    end = frame_number * frame_offset
    begin = int(end - fft_window_size)

    if end == 0:
        return np.zeros((np.abs(begin)), dtype=float)
    elif begin < 0:
        return np.concatenate([np.zeros((np.abs(begin)), dtype=float), audio[0:end]])
    else:
        return audio[begin:end]

def find_top_notes(fft, xf, note_recognition_threshold):
    if np.max(fft.real) < 0.001:
        return []

    lst = [x for x in enumerate(fft.real)]
    lst = sorted(lst, key=lambda x: x[0])
    max_y = max(x[1] for x in lst)
    found_notes = []
    found_note_set = set()

    for idx, value in lst:
        frequency = xf[idx]
        y = value

        # Dopasowanie do najbliższej częstotliwości w posortowanej liście
        closest_freq = find_closest_frequency(frequency)
        name = freq_to_note[closest_freq]

        if name not in found_note_set and y > note_recognition_threshold * max_y:
            found_note_set.add(name)
            found_notes.append([frequency, name, y])

    return found_notes

def process_audio(audio_file, fps, output_name, note_recognition_threshold=0.3):
    agents_notes_results = [[] for _ in FFT_WINDOW_SECONDS]
    big_notes_result = []

    fs, data = wavfile.read(audio_file)
    audio = data.T[0]
    audio_length = len(audio) / fs
    frame_count = int(audio_length * fps)
    frame_offset = int(len(audio) / frame_count)

    print(f"Audio data type: {audio.dtype}")

    for index, agent in enumerate(FFT_WINDOW_SECONDS):
        current_notes_result = []
        fft_window_size = int(fs * agent)

        window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, fft_window_size, False)))
        xf = np.fft.rfftfreq(fft_window_size, 1 / fs)

        max_amplitude = 0
        for frame_number in range(frame_count):
            sample = extract_sample(audio, frame_number, fft_window_size, frame_offset)

            fft = np.fft.rfft(sample * window)
            fft = np.abs(fft).real
            max_amplitude = max(np.max(fft), max_amplitude)

        for frame_number in tqdm.tqdm(range(frame_count)):
            sample = extract_sample(audio, frame_number, fft_window_size, frame_offset)

            fft = np.fft.rfft(sample * window)
            fft = np.abs(fft) / max_amplitude

            top_notes = find_top_notes(fft, xf, note_recognition_threshold)
            current_notes_result.append(top_notes)

        agents_notes_results[index] = current_notes_result.copy()

    for frame_index in range(frame_count):
        frame_notes = []
        frame_result = []
        for agent_notes_result in agents_notes_results:
            for note in agent_notes_result[frame_index]:
                if note not in frame_notes:
                    frame_notes.append(note)

        for frame_note in frame_notes:
            counter = 0
            for agent_notes_result in agents_notes_results:
                for note in agent_notes_result[frame_index]:
                    if frame_note[1] == note[1]:
                        counter += 1
            if counter >= int(np.ceil(len(FFT_WINDOW_SECONDS) / 2)):
                frame_result.append(frame_note)

        big_notes_result.append(frame_result)

    pickle_name = output_name + ".pickle"

    with open(pickle_name, 'wb') as f:
        pickle.dump(big_notes_result, f)
