import timit_stats as ts
import math
from operator import itemgetter


def calc_importance(a_x, a_y):
    delta_ax = [a_x[i]-a_x[i-1] for i in range(2, len(a_x))]
    delta_ay = [a_y[i]-a_y[i-1] for i in range(2, len(a_y))]
    velocity = [math.sqrt(dx**2 + dy**2) for dx, dy in zip(delta_ax, delta_ay)]
    angle = [math.acos((delta_ax[i]*delta_ax[i-1] + delta_ay[i]*delta_ay[i-1])
                        / (math.sqrt(delta_ax[i]**2 + delta_ay[i]**2) *
                           math.sqrt(delta_ax[i-1] ** 2 + delta_ay[i-1] ** 2))) for i in range(1, len(delta_ax))]

    importance = [a/max(angle) - v/max(velocity) for a, v in zip(angle, velocity)]
    return importance, velocity, angle


def S(t, v, m):
    if t == 0:
        return t
    i = t
    acc = v[i]
    while i > 0 and acc < m:
        i -= 1
        acc += v[i]
    return i


def E(t, v, m):
    if t == len(v):
        return t
    i = t
    acc = v[i]
    while i < len(v)-1 and acc < m:
        i += 1
        acc += v[i]
    return i


def find_critical_points(a, params, m):
    a_x = params[a+"_x"]
    a_y = params[a+"_y"]
    imp, vel, angle = calc_importance(a_x, a_y)
    cp = []
    m = m * sum(vel)
    for i in range(len(imp)):
        s = S(i, vel, m)
        e = E(i, vel, m)
        left = [imp[t] for t in range(s, i)]
        right = [imp[t] for t in range(i+1, e)]
        if left + right and imp[i] > max(left + right):
            cp.append(i)
    return cp

def test():
    root_dir = "../USC-TIMIT/EMA/Data/M1"
    index = 0

    t_names, m_names = zip(*ts.list_TIMIT_dir(root_dir))
    trans_fname = t_names[index]
    mat_fname = m_names[index]

    # parse .trans file
    t_starts, t_ends, phonemes, words, sentences = ts.parse_transcription(trans_fname)
    phones = list(set(phonemes))
    # parse .mat file
    params, srates = ts.parse_mat(mat_fname)
    print "Sentence \"{}\" loaded succesfully".format(trans_fname)

    artic = "TT"
    domains = ["_x", "_y"]
    importance, vel, angle = calc_importance(params[artic + domains[0]], params[artic + domains[1]])

    a = "TT"
    m = 0.05 * sum(vel)
    print S(10, vel, m)
    print E(100, vel, m)
    print max(importance[0:144])
    print importance[10]

    print importance[0:10]

    crit_points = find_critical_points(a, params)
    crit_importance = [importance[i] for i in crit_points]
    print crit_points
    return

