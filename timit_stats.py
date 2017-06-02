import os

dir = "../USC-TIMIT/EMA/Data/M1/trans"
trans = os.listdir(dir)

def filter_files(dir):
    return

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

