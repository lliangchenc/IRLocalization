import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
import threading
import numpy as np
from IPython import embed
from utils import *

def plot(data, ax=None, scatter=None):
	quat_arr = []
	radiance_arr = []
	theta_arr = []
	if len(data) != 0:
		for d in data:
			quat_arr.append(d[0])
			radiance_arr.append(d[1])
		vec_origin = normalized(quat_to_mat(quat_arr[0])[1])
		for q in quat_arr:
			mat = quat_to_mat(q)
			vec_forward = normalized(mat[1])
			vec_upper = mat[2]
			sgn = np.sign(np.cross(vec_origin, vec_forward).dot(vec_upper))
			theta_arr.append(np.arccos(vec_forward.dot(vec_origin)) * sgn)

	if ax is not None:
		return ax.scatter(np.degrees(theta_arr), radiance_arr, s=5.0)
	else:
		scatter.set_offsets(np.array([np.degrees(theta_arr), radiance_arr]).T)


def plot_all(data_dict):
	key_cnt = 0
	subplot_base = len(data_dict) * 100 + 10
	for key in data_dict:
		data = data_dict[key]
		key_cnt += 1
		ax = plt.subplot(subplot_base + key_cnt)
		ax.set_title(key)
		plot(data, ax=ax)
	plt.show()

class Visualizer():
	def __init__(self, init_data_dict):
		# Plot Configuration
		self.fig = plt.figure()
		self.axes = {}
		self.data_dict = init_data_dict
		self.scatters = {}

		key_cnt = 0
		subplot_base = len(init_data_dict) * 100 + 10
		for key in init_data_dict:
			key_cnt += 1
			self.axes[key] = plt.subplot(subplot_base + key_cnt)
			self.axes[key].set_xlim(-60, 60)
			self.axes[key].set_ylim(0, 1200)
			self.axes[key].set_title(key)            
			self.scatters[key] = plot(self.data_dict[key], ax=self.axes[key])

	def update_data(self, data):
		self.data_dict = data

	def visualize(self):
		def plot_init():
			# embed()
			return self.scatters.values()
		def plot_update(step):
			scatters = []
			for key in self.data_dict:
				data = self.data_dict[key]
				scatter = self.scatters[key]
				plot(data, scatter=scatter)

			return self.scatters.values()

		ani = animation.FuncAnimation(self.fig, plot_update, init_func=plot_init, frames=1, interval=30, blit=True)
		plt.show()
		
if __name__ == '__main__':
	with open('data/test-multi.pkl', 'rb') as f:
		data_dict = pickle.load(f)
	plot_all(data_dict)
