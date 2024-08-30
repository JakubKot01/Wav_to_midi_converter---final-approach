import wav_reader
import midi_generator
import argparse


def prepare_file_name(file_name):
    if file_name[0] == '.' and file_name[1] == '\\':
        file_name = file_name[2:]

    if file_name[-4] == '.':
        file_name = file_name[:-4]

    return file_name


def main(source_name, bpm, precision, tone, deduce_tone, note_recognition_threshold, fps):
    file_name = prepare_file_name(source_name)
    print(f"processing: {file_name}")

    wav_reader.process_audio(source_name, fps, file_name, note_recognition_threshold)
    midi_generator.generate(file_name, bpm, fps, precision, deduce_tone, tone)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process audio and generate MIDI.")

    parser.add_argument('source_name', type=str, help="The name of the source WAV file.")
    parser.add_argument('--bpm', type=int, default=120, help="Beats per minute for MIDI generation. Default: 120")
    parser.add_argument('--precision', type=int, default=3, choices=[1, 2, 3, 4],
                        help="Precision level (1 (quarter notes), 2 (eighth note), 3 (sixteenth note), or 4 (thirty-second note)) for MIDI generation. Default: 3")
    parser.add_argument('--tone', type=str, default="", help="The musical key (tone) to use.")
    parser.add_argument('--deduce_tone', type=bool, default=False,
                        help="Whether to deduce the tone automatically (True/False). Default: False")
    parser.add_argument('--note_recognition_threshold', type=float, default=0.2,
                        help="Threshold for note recognition in MIDI generation. Recommended in range [0.2, 0.4]. Default: 0.2")
    parser.add_argument('--fps', type=int, default=60, help="Frames per second for audio processing. Default: 60")

    args = parser.parse_args()

    main(args.source_name, args.bpm, args.precision, args.tone, args.deduce_tone, args.note_recognition_threshold, args.fps)