from mido import MidiFile
import argparse

def read_midi(file):
	mid = MidiFile(file)
	print 'Ticks per beat:'
	print mid.ticks_per_beat

	for i, track in enumerate(mid.tracks):
	    print('Track {}: {}'.format(i, track.name))
	    for msg in track:
	        print(msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MIDI File reader.')
    parser.add_argument('--midi-file',
        type = str,
        dest = "midi_file",
        default = "notes.mid",
        help='Track name')
    args = parser.parse_args()
    generate_midi(args.midi_file)