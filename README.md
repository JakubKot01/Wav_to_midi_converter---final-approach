# Wav to midi converter

Originaly, the project was created as a proof of concept for BE's thesis.
It's a tool deducing notes of song coded in .wav files using classic algorithm like FFT and original heuristics.

"The project will continue to be developed in the future."

## Required libraries:
* numpy
* scipy.io
* tqdm
* pickle
* argparse
* mido

## How to use

python .\\manager.py [arguments]
positional arguments:
* source_name path to source file .wav
* bpm Song tempo
  
optional arguments
* -h, --help
* --precision {1,2,3,4} Poziom precyzji:
  * 1 - quarter notes
  * 2 - eight notes
  * 3 - sixteenth notes
  * 4 - 32-notes
  * Default: 3
* --tone TONE Key of song (Currently supporting only minor keys in polish format - please use form "X-moll")
* --deduce_tone DEDUCE_TONE (True | False) - Do you want the program to deduce most propable key?
  * Default: Off
* --note_recognition_threshold NOTE_RECOGNITION_THRESHOLD
* Suggesting to values in range: [0.2, 0.4]
* Default: 0.2
* --fps FPS Number of FPS - amount of samples taken in each second of song
