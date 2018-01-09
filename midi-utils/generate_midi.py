import mido
import argparse
import json
from random import seed,randint
from math import log,ceil
seed(55555)

OFFSET = 1600
MAX_VAL = 10

def split_bits(val):
    return val//128, val%128

def generate_patch(synth_config, zero=False, binary_seq=None):
    patch = []

    if binary_seq is not None:
        binlen = binary_seq[1]
        binstr = bin(binary_seq[0])
        binstr = binstr[2:(2+binlen)]
        if len(binstr) < binlen:
            binstr = '0' * (binlen - len(binstr)) + binstr
        print binstr
        conf_vals = {}
        conf_names = sorted(synth_config.keys())
        for i,conf_name in enumerate(conf_names):
            conf_val = int(binstr[i])
            conf_vals[conf_name] = conf_val
        print conf_vals
    else:
        conf_vals = None

    for control, control_params in synth_config.iteritems():

        param = {'name':control}

        if 'set' in control_params:
            n_vals = len(control_params['set'])
            if zero:
                i_val = 0
            elif conf_vals is not None:
                i_val = conf_vals[control]
            else:
                i_val = randint(0, n_vals-1)
            cc_val = control_params['set'][i_val]
            synth_val = control_params['labels'][i_val]

        elif 'range' in control_params:
            if zero:
                cc_val = 0
                synth_val = 0
            elif 'minmax' in control_params:
                mindom, maxdom = control_params['range']
                minval, maxval = control_params['minmax']
                cc_val = randint(minval, maxval)
                synth_val = (cc_val - mindom) * 10.0 / (maxdom - mindom)
            else:
                minval, maxval = control_params['range']
                cc_val = randint(minval, maxval)
                synth_val = (cc_val - minval) * 10.0 / (maxval - minval)
        else:
            raise ValueError('Input range/set missing')

        param['val'] = synth_val

        if type(control_params['CC']) == int:
            param['cc_msb']  = control_params['CC']
            param['cc_lsb']  = None
            param['val_msb'] = cc_val
            param['val_lsb'] = None

        elif type(control_params['CC']) == list:
            param['cc_msb'] = control_params['CC'][0]
            param['cc_lsb'] = control_params['CC'][1]
            param['val_msb'], param['val_lsb'] = split_bits(cc_val)

        else:
            raise ValueError('Can\'t read CC')

        patch.append(param)

    return(patch)


def add_patch_to_midi(patch, track, time=0):
    first_message = True

    for param in patch:
        if first_message:
            time = time
            first_message = False
        else:
            time = 0
        track.append(
            mido.Message('control_change',
                        control=param['cc_msb'],
                        value=param['val_msb'],
                        time=time))

        if param['cc_lsb'] is not None:
            track.append(
                mido.Message('control_change',
                            control=param['cc_lsb'],
                            value=param['val_lsb'],
                            time=0))


def patches_to_csv(patches, csv_file):
    colnames = [p['name'] for p in patches[0]]

    with open(csv_file, 'w') as f:
        header = ','.join(colnames)
        f.write(header + '\n')

        for patch in patches:

            param_dic = {}
            for param in patch:
                key = param['name']
                value = param['val']
                if type(value) == float or type(value) == int:
                    s_value = str(value)
                elif type(value) == str or type(value) == unicode:
                    s_value = '"' + str(value) + '"'
                else:
                    raise ValueError('Can\'t write csv')
                param_dic[key] = s_value

            values = [str(param_dic[k]) for k in colnames]
            line = ','.join(values)
            f.write(line + '\n')


def generate_midi(midi_file, csv_file,
                    synth_cfg_path, note, n_notes, tempo, duration, seq):

    # Loads the synth config
    with open(synth_cfg_path) as synth_cfg_file:
        synth_cfg = json.load(synth_cfg_file)

    if seq:
        bin_seq_len = len(synth_cfg)
        print 'Will enumerate over', str(bin_seq_len), 'bits'

    # Sets up the tracks
    mid = mido.MidiFile(type = 0, ticks_per_beat=9600)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Meta messages
    track.append(mido.MetaMessage('smpte_offset',
            frame_rate=25, hours=33, minutes=0, seconds=0,
            frames=0, sub_frames=0, time=0
    ))
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    track.append(mido.MetaMessage('time_signature',
                                numerator=4,denominator=4,
                                clocks_per_click=24,
                                notated_32nd_notes_per_beat=8,
                                time=0))

    patches = []
    for i in range(n_notes):

        # Reinit
        if i == 0:
            stime = 0
        else:
            stime = OFFSET
        patch0 = generate_patch(synth_cfg, zero=True)
        add_patch_to_midi(patch0, track, time = stime)

        # New patch
        if not seq:
            patch = generate_patch(synth_cfg)
        else:
            patch = generate_patch(synth_cfg, binary_seq=(i,bin_seq_len))
        add_patch_to_midi(patch, track, time = OFFSET//2)
        patches.append(patch)

        # Sends and releases the note
        track.append(mido.Message('note_on',  note=note,
                                velocity=120, time=OFFSET//2))

        track.append(mido.Message('note_off', note=note,
                                velocity=120, time=duration - OFFSET * 2))


    mid.save(midi_file)
    patches_to_csv(patches, csv_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MIDI File generator.')

    parser.add_argument('--midi-file',
        type = str,
        dest = "midi_file",
        default = "notes.mid",
        help='Track name')

    parser.add_argument('--csv-file',
        type = str,
        dest = 'csv_file',
        default = "notes.csv",
        help='Track name')

    parser.add_argument('--synth-config',
        type = str,
        dest = "synth_cfg",
        default = "../synth-config/subphatty_params.json",
        help='JSON description of the synth pameters')

    parser.add_argument('--note',
        type = int,
        dest = "note",
        default = 60,
        help='MIDI note')

    parser.add_argument('--n_notes',
        type = int,
        dest = "n_notes",
        default = 15,
        help='Number of notes')

    parser.add_argument('--tempo',
        type = int,
        dest = "tempo",
        default = 1000000,
        help='Track tempo')

    parser.add_argument('--duration',
        type = int,
        dest = "duration",
        default = 9600,
        help='Note duration')

    parser.add_argument('--seq',
        type = bool,
        dest = "seq",
        default = False,
        help='Generate sequence')

    args = parser.parse_args()

    generate_midi(args.midi_file, args.csv_file, args.synth_cfg,
                    args.note, args.n_notes, args.tempo, args.duration,
                    args.seq)