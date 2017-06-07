import os
import scipy.io as sio
import gesture as ges
import timit_stats as ts
import math


trans_dir = "../USC-TIMIT/EMA/Data/M1/trans"
mat_dir = "../USC-TIMIT/EMA/Data/M1/mat"
trans = os.listdir(trans_dir)


def parse_sentence(mat_fname, trans_fname):
    return
    # parse trans file
    t_starts, t_ends, phonemes, words, sentences = ts.parse_transcription(trans_fname)
    phones = list(set(phonemes))

    # parse mat file
    params, srates = ts.parse_mat(mat_fname)

    for ph in phones:
        gestures[ph] = ges.Gesture(ph)

    # loop through phones
    for i in range(len(t_starts)):
        t_s = float(t_starts[i])
        t_e = float(t_ends[i])
        ph = phonemes[i]
        samples = {}
        # loop through ema from t_s up to t_e
        for p in params:
            rate = srates[p]
            i_start = int(t_s * rate)
            i_end = int(t_e * rate)
            # try to filter only samples considered as target
            length = i_end - i_start
            samples[p] = [v for v in params[p][i_start + length / 4:i_start + length / 4 * 3] if not math.isnan(v)]
        gestures[ph].add_samples(samples)
    return gestures