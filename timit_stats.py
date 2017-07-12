import os
import scipy.io as sio
import gesture as ges
import math
import critical_point as cp
import pickle
import numpy as np
from scipy import interpolate

trans_dir = "../USC-TIMIT/EMA/Data/M1/trans"
mat_dir = "../USC-TIMIT/EMA/Data/M1/mat"
trans = os.listdir(trans_dir)


def save_obj(obj, name ):
    if not os.path.exists('obj/'):
        os.makedirs("obj")
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def list_TIMIT_dir(root_dir):
    trans_dir = os.path.join(root_dir, "trans")
    mat_dir = os.path.join(root_dir, "mat")
    return [(os.path.join(trans_dir, fname),
              os.path.join(mat_dir, os.path.splitext(fname)[0] + ".mat")) for fname in os.listdir(trans_dir)]


def parse_transcription(fname):
    t_starts = []
    t_ends = []
    phonemes = []
    words = []
    sentences = []
    with open(fname) as f:
        content = f.readlines()
    for line in content:
        word_list = line.split(',')
        t_starts.append(float(word_list[0]))
        t_ends.append(float(word_list[1]))
        phonemes.append(word_list[2])
        words.append(word_list[3])
        sentences.append(word_list[4])
    return t_starts, t_ends, phonemes, words, sentences


def parse_trans_corpus(dir):
    t_starts = []
    t_ends = []
    phonemes = []
    words = []
    sentences = []
    for fname in trans:
        t_s, t_e, ph, w, s = parse_transcription(dir + '/' + fname)
        t_starts.extend(t_s)
        t_ends.extend(t_e)
        phonemes.extend(ph)
        words.extend(w)
        sentences.extend(s)
    return t_starts, t_ends, phonemes, words, sentences


def parse_mat(mat_fname):
    # load mat file
    mat_contents = sio.loadmat(mat_fname)

    name = os.path.splitext(os.path.basename(mat_fname))[0]
    data = mat_contents[name]
    rows = len(data[0])
    params = {}
    srates = {}
    for r in range(1,rows):
        p = data[0,r][0][0]
        params[p + "_x"] = []
        params[p + "_y"] = []
        params[p + "_z"] = []
        srates[p + "_x"] = data[0,r][1][0][0]
        srates[p + "_y"] = data[0,r][1][0][0]
        srates[p + "_z"] = data[0,r][1][0][0]
        sample_size = len(data[0,r][2])
        for i in range(sample_size):
            params[p + "_x"].append(data[0, r][2][i][0])
            params[p + "_y"].append(data[0, r][2][i][1])
            params[p + "_z"].append(data[0, r][2][i][2])
    return params, srates


def calc_gestures(mat_fname, trans_fname, filter_critical_points=False, m=0.05):
    gestures = {}

    # parse trans file
    t_starts, t_ends, phonemes, words, sentences = parse_transcription(trans_fname)
    phones = list(set(phonemes))

    # parse mat file
    params, srates = parse_mat(mat_fname)

    critical_points = set()
    if filter_critical_points:
        param_names = params.keys()
        param_names = [p[:-2] for p in param_names]
        param_names = list(set(param_names))
        for p in param_names:
            critical_points.update(cp.find_critical_points(p, params, m))


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
            if filter_critical_points:
                samples[p] = [v for v, i in zip(params[p][i_start:i_start+length], range(i_start, i_end)) if
                              not math.isnan(v) and i in critical_points]
            else:
                samples[p] = [v for v in params[p][i_start:i_start + length] if not math.isnan(v)]
        gestures[ph].add_samples(samples)
    return gestures


def normalize_gestures(gestures):
    g = gestures.itervalues().next()
    params = g.params.keys()
    p_max = {p: max(g.params[p]) for p in params}
    p_min = {p: min(g.params[p]) for p in params}
    for p in params:
        for g in gestures:
            p_max[p] = max(p_max[p], max(gestures[g].params[p]))
            p_min[p] = min(p_min[p], min(gestures[g].params[p]))

    norm_gestures = gestures.copy()
    for g in norm_gestures:
        for p, v in norm_gestures[g].params.items():
            norm_gestures[g].params[p] = [(i - p_min[p])/(p_max[p]-p_min[p]) for i in v]
    return norm_gestures, p_max, p_min


def parse_corpus(dir):
    phonemes_dict = {}
    gestures = {}
    fnames = list_TIMIT_dir(dir)

    for trans_fname, mat_fname in fnames:
        # parse transcription
        t_starts, t_ends, phonemes, words, sentences = parse_transcription(trans_fname)

        # parse mat file
        params, srates = parse_mat(mat_fname)

        # loop trough phonemes
        for t_start, t_end, phoneme_name in zip(t_starts, t_ends, phonemes):
            phoneme_params = {}
            for p in params:
                sampling_rate = srates[p]
                sample_start = int(t_start * sampling_rate)
                sample_end = int(t_end * sampling_rate)
                trajectory = params[p][sample_start:sample_end]
                phoneme_params[p] = trajectory
            phoneme = ges.Phoneme(phoneme_name, phoneme_params, (t_start, t_end), trans_fname)

            if phoneme_name not in gestures:
                gestures[phoneme_name] = ges.Gesture(phoneme_name)
            gestures[phoneme_name].add(phoneme)
    #         # add phoneme to dict
    #         if phoneme_name not in phonemes_dict:
    #             phonemes_dict[phoneme_name] = [phoneme]
    #         else:
    #             phonemes_dict[phoneme_name].append(phoneme)
    #
    # for ph in phonemes_dict:
    #     print ph, len(phonemes_dict[ph])
    #
    # for fname in os.listdir(trans_dir):
    #     fname = os.path.splitext(fname)[0]
    #     print "Analyze ", fname
    #     t_fname = os.path.join(trans_dir, fname + ".trans")
    #     mat_fname = os.path.join(mat_dir, fname + ".mat")
    #     # parse trans file
    #     t_starts, t_ends, phonemes, words, sentences = parse_transcription(trans_fname)
    #     phones = list(set(phonemes))
    #
    #     # parse mat file
    #     params, srates = parse_mat(mat_fname)

    return gestures


def scale_phonemes(num_scale, gestures):
    scaled_gestures = {}
    for g in gestures:
        scaled_gestures[g] = ges.Gesture(g)
        phonemes = gestures[g].phonemes
        for phoneme in phonemes:
            params = phoneme.params
            params_scaled = {}
            num_before = len(params["TT_x"])
            if num_before < 4:
                continue
            t_before = np.linspace(0, num_before, num_before)
            t_before_scaled = [t * num_scale / num_before for t in t_before]
            for p in params:

                # interpolate
                k = min(3, len(t_before_scaled)-1)
                tck = interpolate.splrep(t_before_scaled, params[p], s=0, k=k)
                t_after = np.linspace(0, num_scale, num_scale)
                params_scaled[p] = interpolate.splev(t_after, tck, der=0)
            scaled_phoneme = ges.Phoneme(g, params_scaled, phoneme.time, phoneme.source)
            scaled_gestures[g].add(scaled_phoneme)
    return scaled_gestures


def test_parse_corpus():
    root_dir = "../USC-TIMIT/EMA/Data/M1"

    gestures = parse_corpus(root_dir)
    save_obj(gestures, "gestures")
    print "Corpus parsed"

    # gestures = load_obj("gestures")
    scaled_gestures = scale_phonemes(100, gestures)
    save_obj(scaled_gestures, "scaled_gestures")
    print "Gestures scaled"
    return


def test():

    gestures = {}

    for fname in os.listdir(trans_dir):
        fname = os.path.splitext(fname)[0]
        print "Analyze ", fname
        t_fname = os.path.join(trans_dir, fname + ".trans")
        mat_fname = os.path.join(mat_dir, fname + ".mat")
        gest = calc_gestures(mat_fname, t_fname)
        for g in gest:
            if g not in gestures:
                gestures[g] = ges.Gesture(g)
            gestures[g].extend(gest[g])

    for g_name, g in gestures.items():
        print g_name
        print len(g.params["LL_x"])
        g_m = g.get_mean()
        print g_m
        g_v = g.get_variance()
        print g_v

    norm_gest, _, _ = normalize_gestures(gestures)

    for g_name, g in norm_gest.items():
        print g_name
        print len(g.params["LL_x"])
        g_m = g.get_mean()
        print g_m
        g_v = g.get_variance()
        print g_v
    return


def find_weights():
    import matplotlib.pyplot as plt


    root_dir = "../USC-TIMIT/EMA/Data/M1"
    index = 10

    t_names, m_names = zip(*list_TIMIT_dir(root_dir))
    trans_fname = t_names[index]
    mat_fname = m_names[index]

    gestures = {}
    means = {}  # key : param_name, value: dict(ges, val)
    variances = {}  # key : param_name, value: dict(ges, val)

    articulators = ["LL", "UL", "TT", "TB", "TD", "JAW"]
    domains = ["_x", "_y"]
    param_names = [a + d for a in articulators for d in domains]

    for i in range(len(t_names)):
        t_fname = t_names[i]
        mat_fname = m_names[i]
        gest = calc_gestures(mat_fname, t_fname, filter_critical_points=False, m=0.05)
        for g in gest:
            if g not in gestures:
                gestures[g] = ges.Gesture(g)
            gestures[g].extend(gest[g])
    print "gestures calculation finished"

    gestures_norm, p_max, p_min = normalize_gestures(gestures)

    # for p in param_names:
    #     means[p] = {}
    #     variances[p] = {}

    for g in gestures_norm:
        variances[g] = {}
        means[g] = {}
        g_m = gestures_norm[g].get_mean()
        g_v = gestures_norm[g].get_variance()
        for p in param_names:
            means[g][p] = g_m[p] * (p_max[p] - p_min[p]) + p_min[p]
            variances[g][p] = g_v[p]


    print "Means and variances calculated succesfully"
    for g in gestures_norm:
        print "{}    /////////////////////////////////".format(g)
        for k,v in variances[g].items():
            print "{} : {:.2f}".format(k, math.exp(-50.0*v))


# find_weights()

test_parse_corpus()