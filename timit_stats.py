import os
import scipy.io as sio
import gesture as ges

trans_dir = "../USC-TIMIT/EMA/Data/M1/trans"
mat_dir = "../USC-TIMIT/EMA/Data/M1/mat"
trans = os.listdir(trans_dir)


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
        t_starts.append(word_list[0])
        t_ends.append(word_list[1])
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
        # print "Articulator = ",data[0,r][0][0]
        # print "SRate = ", data[0,r][1][0][0]
        # print "Samples len = ",len(data[0,r][2])
        for i in range(sample_size):
            params[p + "_x"].append(data[0, r][2][i][0])
            params[p + "_y"].append(data[0, r][2][i][1])
            params[p + "_z"].append(data[0, r][2][i][2])
    return params, srates


def calc_gestures(mat_fname, trans_fname):
    gestures = {}

    # parse trans file
    t_starts, t_ends, phonemes, words, sentences = parse_transcription(trans_fname)
    phones = list(set(phonemes))

    # parse mat file
    params, srates = parse_mat(mat_fname)

    for ph in phones:
        gestures[ph] = ges.Gesture(ph)

    # loop through phones
    for i in range(len(t_starts)):
        t_s = float(t_starts[i])
        t_e = float(t_ends[i])
        ph = phonemes[i]

        # loop through ema from t_s up to t_e
        for p in params:
            rate = srates[p]
            i_start = int(t_s * rate)
            i_end = int(t_e * rate)
            gestures[ph].add_samples(p, params[p][i_start:i_end])

    return gestures


trans_names = os.listdir(trans_dir)
fname = os.path.splitext(trans_names[1])[0]
t_fname = os.path.join(trans_dir, fname + ".trans")
mat_fname = os.path.join(mat_dir, fname + ".mat")
ges = calc_gestures(mat_fname, t_fname)
for g_name, g in ges.items():
    print g_name
    print len(g.params["LL_x"])
    g_m = g.get_mean()
    print g_m
    g_v = g.get_variance()
    print g_v

print ges.keys()
print len(ges["iy"].params["TT_z"])
print len(ges["iy"].params["LL_x"])
print len(ges["iy"].params["TT_y"])