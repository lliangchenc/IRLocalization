import pickle
import numpy as np
from visualize import DataCollectionVisualizer
from utils import *
from time import sleep
import threading
from scipy.optimize import leastsq
import matplotlib.pyplot as plt

with open('data/test-0119-03.pkl', 'rb') as f:
    data = pickle.load(f)

quats = []
for d in data['quats']:
    quat, idx = d
    quats.append(quat)
angles = quats_to_angles(quats)
angles = np.radians(angles) + 0.15

# visualizer = DataCollectionVisualizer()

# def thread_runner():
#     for delay in np.arange(-20, 0):
#         radiances = []
#         for d in data['quats']:
#             _, idx = d
#             radiances.append(data['radiances'][idx - delay])
#         assert(len(quats) == len(radiances))
#         visualizer.update_data({'quats': quats, 'radiances': radiances})
#         sleep(2)

# t = threading.Thread(target=thread_runner)
# t.start()

# it turns out that -10 is an appropiate offset
OFFSET = -10
radiances = []
for d in data['quats']:
    _, idx = d
    radiances.append(data['radiances'][idx - OFFSET])
radiances = 1023 - np.array(radiances)
# visualizer.update_data({'quats': quats, 'radiances': 1023 - np.array(radiances)})
# visualizer.visualize()

def fit_func(angles, a, b, c, sigma):
    val = a * np.exp(-np.tan(angles - b) ** 2 / sigma) \
        + a * np.exp(-np.tan(angles + b) ** 2 / sigma) + c
    # print(val)
    return val

def residual_func(params, angles, radiances):

    val = (fit_func(angles, *params) - radiances) ** 2 / len(angles) + sigma * 10000
    print(np.mean(val), np.mean(val) - sigma * 10000)
    return val

# a, b, c, sigma = 677, 0.83, 100, 0.0094
a, b, c, sigma = 6.77115931e+02, 8.34383657e-02, 100, 9.45940256e-03

plt.figure()
plt.scatter(angles, radiances, s=5.0)
popt, pcov = leastsq(residual_func, [a, b, c, sigma], args=(angles, radiances))
print(popt)
angle_arr = np.linspace(-0.5, 0.5, 200)
plt.plot(angle_arr, fit_func(angle_arr, *popt))
plt.plot(angle_arr, fit_func(angle_arr, a, b, c, sigma))
plt.show()
