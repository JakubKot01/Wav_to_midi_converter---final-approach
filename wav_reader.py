import os
import shutil
import numpy as np
from scipy.io import wavfile
import tqdm
import pickle

# Konfiguracja
FFT_WINDOW_SECONDS = [0.05, 0.2, 0.3, 0.4, 0.6]  # ile sekund audio składa się na okno FFT
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# Przygotowanie katalogu

def prepare_directory(directory):
    if directory == os.getcwd():
        return
    shutil.rmtree(directory, ignore_errors=True)
    os.makedirs(directory, exist_ok=True)


# Ekstrakcja próbki audio
def extract_sample(audio, frame_number, fft_window_size, frame_offset):

    end = frame_number * frame_offset
    begin = int(end - fft_window_size)

    if end == 0:
        # We have no audio yet, return all zeros (very beginning)
        return np.zeros((np.abs(begin)), dtype=float)
    elif begin < 0:
        # We have some audio, padd with zeros
        return np.concatenate([np.zeros((np.abs(begin)), dtype=float), audio[0:end]])
    else:
        # Usually this happens, return the next sample
        return audio[begin:end]


# Znalezienie głównych nut w FFT
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
        n = freq_to_number(frequency)
        n0 = int(round(n))
        name = note_name(n0)

        if name not in found_note_set and y > note_recognition_threshold * max_y:
            found_note_set.add(name)
            found_notes.append([frequency, name, y])

    return found_notes


# Konwersje częstotliwości i numerów nut
def freq_to_number(f):
    return 69 + 12 * np.log2(f / 440.0) if f > 0 else 0


def number_to_freq(n):
    return 440 * 2.0 ** ((n - 69) / 12.0)


def note_name(n):
    number = int(n / 12 - 1)
    if number >= 0:
        return NOTE_NAMES[n % 12] + str(number)
    return NOTE_NAMES[n % 12] + '0'


# Główna funkcja przetwarzania audio
def process_audio(audio_file, fps, output_name, note_recognition_threshold=0.3):

    working_directory = os.getcwd()
    content_directory = os.path.join(working_directory, "Content")

    prepare_directory(content_directory)
    agents_notes_results = [[] for _ in FFT_WINDOW_SECONDS]
    big_notes_result = []

    fs, data = wavfile.read(audio_file)
    audio = data.T[0]
    print(audio)
    audio_length = len(audio) / fs
    print(audio_length)
    frame_count = int(audio_length * fps)
    frame_offset = int(len(audio) / frame_count)

    # Sprawdzenie typu danych i zakresu wartości
    print(f"Audio data type: {audio.dtype}")
    print(f"Sample values (first 10 samples): {audio[:10]}")

    for index, agent in enumerate(FFT_WINDOW_SECONDS):
        current_notes_result = []
        # Odczyt pliku audio
        fft_window_size = int(fs * agent)

        # Okno FFT i częstotliwości
        window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, fft_window_size, False)))
        xf = np.fft.rfftfreq(fft_window_size, 1 / fs)

        # results = []

        max_amplitude = 0
        # Przetwarzanie każdej ramki
        for frame_number in tqdm.tqdm(range(frame_count)):
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

    print(pickle_name)
    with open(pickle_name, 'wb') as f:
        pickle.dump(big_notes_result, f)
