# The Secret Sauce Project

The aim of the Secret Sauce project is to automatically reverse engineer studio sounds, with a focus on guitar effects and synthesizers. Give the model a reference sound, and it will tell you how to reproduce it.

More details [here](http://127.0.0.1:4000/2018/01/01/Secret-Sauce-data.html)

- midi-utils: tools to generate random MIDI patches and tracks
- audio-utils: basic post-processing for generated audio tracks
- synth-config: JSON description of MIDI mappings and value ranges
- data: meta-data used for sound generation
- models: Jupyter notebooks for the experiments described in the [blog post](http://127.0.0.1:4000/2018/01/13/Secret-Sauce-First-Results.html)

Sound generation relies on the libraries `mido` for MIDI and `sox` for audio.
The models require `jupyter`, `keras`, `tensorflow`, `numpy`, `pandas` and the great `librosa`.
