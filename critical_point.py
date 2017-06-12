import timit_stats as ts
import math


def calc_importance(a_x, a_y):
    delta_ax = [a_x[i]-a_x[i-1] for i in range(2, len(a_x))]
    delta_ay = [a_y[i]-a_y[i-1] for i in range(2, len(a_y))]
    velocity = [math.sqrt(dx**2 + dy**2) for dx, dy in zip(delta_ax, delta_ay)]
    angle = [math.atan2(dy,dx) for dx, dy in zip(delta_ax, delta_ay)]
    importance = [a/max(angle) - v/max(velocity) for a, v in zip(angle, velocity)]
    return importance, velocity, angle

def test():
    return

