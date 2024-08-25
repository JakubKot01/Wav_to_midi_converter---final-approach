import wav_reader
import midi_generator

content_table = ["Otherside - Bass.wav",
                 "Otherside - Instrumental.wav",
                 "Otherside - Vocals.wav"]


def prepare_file_name(file_name):
    if file_name[0] == '.' and file_name[1] == '\\':
        file_name = file_name[2:]

    if file_name[-4] == '.':
        file_name = file_name[:-4]

    return file_name


for file in content_table:
    file_name = prepare_file_name(file)
    print(f"processing: {file_name}")

    # wav_reader.process_audio(file, 60, file_name)
    test = file_name.split(" - ")[1]
    if test == "Vocals":
        midi_generator.generate(file_name, 123, 60, precision=3)
    else:
        midi_generator.generate(file_name, 123, 60, precision=2)