import wav_reader

content_table = ["Blood Upon the Snow - Bass.wav",
                 "Blood Upon the Snow - Drums.wav",
                 "Blood Upon the Snow - Instrumental.wav",
                 "Blood Upon the Snow - Vocals.wav"]

for file in content_table:
    print(f"processing: {file.split(" - ")[1][:-4]}")
    wav_reader.process_audio(file, 60)
