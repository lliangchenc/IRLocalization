""" Train energy function
Currently only support offline training.

"""

import numpy as np
np.set_printoptions(precision=3)
import pickle
import matplotlib.pyplot as plt
from server import energy_func

FLAG_START	= 0
FLAG_END	= 1

LENGTH_GT	= 4		# the distance from left to right
FOREARM_LEN = 0.3	# a simple correction of hand movement in collecting data (elbow fixed, forearm rotates)

data = []

def process():
	global vi_list, brightness_list
	def is_flag(frame):
		return len(frame) == 0

	# v_ret = None
	# break_flag = False

	# while not break_flag:
	# 	for i in range(len(data)):
	# 		frame = data[i]
	# 		if is_flag(frame):
	# 			if flag == FLAG_START:
	# 				brightness_list = []
	# 				vi_list = []
	# 				break_flag = True
	# 			if i == len(data) - 1: # last frame, use vi of previous frame as returned vector
	# 				v_ret = data[i - 1][0]
	# 			else:
	# 				v_ret = data[i + 1][0]
	# 			continue
	# 		vi_list.append(np.array(frame[0]))
	# 		brightness_list.append(frame[1])

	flag = FLAG_START
	for i in range(len(data) - 1):
		frame = data[i]
		vi_list.append(np.array(frame[0]))
		brightness_list.append(frame[1])

	v_lt = np.array(data[0][0])
	v_rt = np.array(data[-1][0])
	return v_lt / np.linalg.norm(v_lt), v_rt / np.linalg.norm(v_rt)


if __name__ == '__main__':
	with open('samples/samples-energy-no-line.pkl', 'rb') as f:
		data = pickle.load(f)	

	brightness_list = []
	vi_list = []

	# v_lt = wait_for_flag(FLAG_START)
	# v_rt = wait_for_flag(FLAG_END)
	v_lt, v_rt = process()
	print(f'v_lt: {v_lt}')
	print(f'v_rt: {v_rt}')

	cos_theta = np.dot(v_lt, v_rt)
	tan_theta_2 = ((1 - cos_theta) / (1 + cos_theta)) ** 0.5
	h0 = LENGTH_GT / 2. / tan_theta_2 - FOREARM_LEN
	print(f"h0: {h0}")
	v0 = (v_lt + v_rt) / np.linalg.norm(v_lt + v_rt)
	print(f'v0: {v0}')

	cos_theta_i_arr = np.dot(np.array(vi_list), v0)
	theta_i_arr = np.arccos(cos_theta_i_arr)	# assume the light source is symmetric

	hi_arr = h0 / cos_theta_i_arr
	# origin_brightness_arr = (hi_arr ** 2) * brightness_list

	plt.figure()
	# plt.scatter(np.degrees(theta_i_arr), origin_brightness_arr)
	plt.scatter(np.degrees(theta_i_arr), brightness_list)
	x = np.linspace(0, np.radians(90), 1000)
	plt.plot(np.degrees(theta_i_arr), 100 * energy_func(theta_i_arr, hi_arr))
	plt.show()
