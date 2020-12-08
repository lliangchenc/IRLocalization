"""Evaluate the performance of localization"""

import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
from server import predict

WINDOW_SIZE = 20

v0_list = []
v0_gt_list = []
vi_list = []

with open('samples.pkl', 'rb') as f:
	# data format: [IMU vec (3-dim tuple), distance, gt vec (3-dim tuple)]
	data = pickle.load(f)
	v0 = np.array([1,1,1])
	while len(data) > 0:
		data_slice = data[:WINDOW_SIZE]
		if (len(data_slice) == WINDOW_SIZE):
			vi = np.mean(np.array([x[0] for x in data_slice]), axis=0)
			v0, v0_gt = predict(data_slice, v0)
			vi_list.append(vi)
			v0_list.append(v0)
			v0_gt_list.append(v0_gt)
		data = data[WINDOW_SIZE:]

v0_arr = np.array(v0_list)
v0_gt_arr = np.array(v0_gt_list)
vi_arr = np.array(vi_list)

theta_list = []
delta_theta_list = []
delta_dis_list = []

for i in range(len(v0_arr)):
	v0 = v0_arr[i]
	v0_gt = v0_gt_arr[i]
	vi = vi_arr[i]
	v0_norm = np.linalg.norm(v0)
	v0_gt_norm = np.linalg.norm(v0_gt)
	vi_norm = np.linalg.norm(vi)

	theta_list.append(np.arccos(np.dot(v0_gt / v0_gt_norm, vi / vi_norm)))
	delta_theta_list.append(np.arccos(np.dot(v0_gt / v0_gt_norm, v0 / v0_norm)))
	delta_dis_list.append(np.abs(v0_norm - v0_gt_norm))

plt.figure()
plt.title("Degree Delta")
plt.scatter(np.degrees(theta_list), delta_theta_list)
plt.show()

plt.figure("Distance Delta")
plt.scatter(np.degrees(theta_list), delta_dis_list)
plt.show()
