import matplotlib .pyplot as plt
import math
class Gesture(object):

    def __init__(self, name):
        self.name = name
        self.phonemes = []
        self.mean = None
        self.variance = None

    def add(self, phoneme):
        self.phonemes.append(phoneme)
        self.mean = None
        self.variance = None

    def add_samples(self, samples):
        for ph in samples:
            self.phonemes
        # for k, v in samples.items():
        #     if any([math.isnan(val) for val in v]):
        #         raise ValueError("NaN found in samples")
        #     if k not in self.params:
        #         self.params[k] = []
        #     self.params[k].extend(v)

    def extend(self, phonemes):
        self.phonemes.extend(phonemes)
        self.mean = None
        self.variance = None

    # def get_scaled(self, num_samples):
    #     scaled = []
    #     for phone in self.phonemes:
    #         scaled.append(phone.scale(num_samples))
    #     return scaled

    def get_mean(self):
        if self.mean is not None:
            return self.mean
        mean = {}
        variance = {}

        params = self.phonemes[0].params.keys()
        for p in params:
            mean[p] = 0.0
            variance[p] = 0.0
            num_samples = 0
            for phoneme in self.phonemes:
                if any([math.isnan(v) for v in phoneme.params[p]]):
                    continue
                mean[p] += sum(phoneme.params[p])
                variance[p] += sum([v**2 for v in phoneme.params[p]])
                num_samples += len(phoneme.params[p])
            mean[p] /= num_samples
            variance[p] = variance[p]/num_samples - mean[p]**2
        self.mean = mean
        self.variance = variance
        return self.mean

    def get_variance(self):
        if self.variance is not None:
            return self.variance
        self.get_mean()
        return self.variance


class Phoneme:

    def __init__(self, name, params, time, source=""):
        self.name = name
        self.source = source
        self.time = time
        self.params = params

