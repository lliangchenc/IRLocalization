import matplotlib.pyplot as plt
import numpy as np
import math


def energy_func(theta, d, sigma=0.2):
	return 1.0 / sigma * np.exp(- np.tan(theta) ** 2 / sigma ** 2) / d ** 2

def plot():
	theta_arr = np.linspace(-90, 90, 100)
	d = 3
	plt.figure()
	plt.plot(theta_arr, energy_func(np.radians(theta_arr), d))
	plt.show()

if __name__ == '__main__':
	plot()
