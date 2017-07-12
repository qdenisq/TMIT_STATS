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


def get_target_trajectories(trans_fname, means, rate=200.0):
    # parse trans file
    t_starts, t_ends, phonemes, words, sentences = ts.parse_transcription(trans_fname)

    param_names = means.keys()

    num_samples = t_ends[-1] * rate
    trajectories = {}
    for p in param_names:
        trajectories[p] = []
        traj = []
        cur_pos = 0.0
        for i in range(len(phonemes)):
            target = means[p][phonemes[i]]
            phone_length = (t_ends[i] - t_starts[i])*rate
            traj = [means[p][phonemes[i]]]*int(phone_length)
            trajectories[p].extend(traj)
    return trajectories


def estimate_trajectory(trans_fname, means, variances, rate=200.0):
    # parse trans file
    t_starts, t_ends, phonemes, words, sentences = ts.parse_transcription(trans_fname)

    param_names = means.keys()

    num_samples = t_ends[-1]*rate
    trajectories = {}
    for p in param_names:
        trajectories[p] = []
        traj = []
        cur_pos = 0.0
        for i in range(len(phonemes)):
            target = means[p][phonemes[i]]
            variance = variances[p][phonemes[i]]
            imp0 = math.exp(-50*variance)
            phone_length = (t_ends[i] - t_starts[i])
            tau = max(0.002, phone_length / 10)
            tau = min(0.005, tau)
            for t in range (int(t_starts[i]*rate), int(t_ends[i]*rate)):
                imp = imp0 - imp0 * math.exp(-1.0 * 20.0 / 2.0 * pow(float(t) / rate - t_starts[i], 2) / tau)
                - imp0 * math.exp(-1.0 * 10.0 / 2.0 * pow(float(t) / rate - t_ends[i], 2) / tau)
                if imp < 0.0:
                    imp = 0.0
                delta_pos = (target - cur_pos)*imp
                cur_pos += delta_pos
                trajectories[p].append(cur_pos)
            # phone_length = (t_ends[i] - t_starts[i])*rate
            # traj = [means[p][phonemes[i]]]*int(phone_length)
            # trajectories[p].extend(traj)
    return trajectories