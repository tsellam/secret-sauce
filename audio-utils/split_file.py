import sox
import argparse

def split_track(audio_file, duration, offset, prefix):
	print 'Chunks duratiom:'
	print duration

	total_duration = float(sox.core.soxi(audio_file, 'D'))
	print 'Total duration:', total_duration, 'seconds'

	s = 0
	i = 0
	while s < total_duration:
		if i % 250 == 0 and i > 0:
			print 'Chunk #' + str(i)
			print 'Offset', s, 'out of', total_duration
		start = s + (offset/1000.0)
		end   = s + duration
		transformer = sox.Transformer()
		transformer.trim(start, end)
		transformer.build(audio_file, prefix + str(i) + '.wav')
		s += duration
		i += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Audio File reader.')
    parser.add_argument('--audio-file',
        type = str,
        dest = "audio_file",
        default = "track.wav",
        help='Track file name')
    parser.add_argument('--out-file-prefix',
        type = str,
        dest = "out_prefix",
        default = "out",
        help='Output file name prefix')
    parser.add_argument('--L',
        type = float,
        dest = "duration",
        default = 1,
        help='Chunk duration (s)')
    parser.add_argument('--o',
        type = float,
        dest = "offset",
        default = 0,
        help='Chunk offset (ms)')

    args = parser.parse_args()
    split_track(args.audio_file, args.duration, args.offset, args.out_prefix)