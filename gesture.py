import matplotlib .pyplot as plt
import math
class Gesture(object):

    def __init__(self, name):
        self.name = name
        self.params = {}

    def add_samples(self, samples):
        for k, v in samples.items():
            if any([math.isnan(val) for val in v]):
                raise ValueError("NaN found in samples")
            if k not in self.params:
                self.params[k] = []
            self.params[k].extend(v)

    def extend(self, g):
        self.add_samples(g.params)

    def get_mean(self):
        mean = {}
        for p in self.params:
            mean[p] = sum(self.params[p]) / len(self.params[p])
        return mean

    def get_variance(self):
        variance = {}
        mean = self.get_mean()
        for p in self.params:
            variance[p] = 0.0
            for v in self.params[p]:
                variance[p] += v ** 2
        for p in variance:
            variance[p] = variance[p] / len(self.params[p]) - mean[p] ** 2
        return variance