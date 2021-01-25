#!/usr/bin/env python3

import socket
import sys
import serial
import threading
import argparse
from threading import Lock
import pickle
import numpy as np
import time
import math
from scipy.optimize import leastsq
from window import Window
from visualize import DataCollectionVisualizer, LocalizationVisualizer
from utils import *

HOST = '0.0.0.0'
PORT = 3528
SERIAL_PORT = '/dev/cu.usbmodem142101'
WINDOW_SIZE = 10
PRED_WIN_SIZE = 20

class Server():
	def __init__(self):
		self.serial_window = Window(WINDOW_SIZE)
		self.ser = serial.Serial(SERIAL_PORT)
		self.lock = Lock()
		self.data = {
			'quats': [],
			'radiances': [],
			'vec': None
		}
		# self.visualizer = DataCollectionVisualizer()
		self.visualizer = LocalizationVisualizer()
		self.raw_data = {
			'quats': [],
			'radiances': []
		}
		self.energy_func = self.__energy_func

	def save_data(self, path=None):
		if path: 
			with open(path, 'wb') as f:
				# pickle.dump(self.data, f)
				pickle.dump(self.raw_data, f)

	def start_serial_thread(self):
		t = threading.Thread(target=self.__recv_data_from_serial, daemon=True)
		t.start()

	def __recv_data_from_serial(self):
		while True:
			buf = self.ser.readline().decode()[:-2]	# strip '\r\n'
			self.lock.acquire()
			if len(buf) > 0:
				self.serial_window.push(float(buf))
				self.raw_data['radiances'].append(float(buf))
			self.lock.release()

	def start_socket_thread(self):
		t = threading.Thread(target=self.__recv_data_from_socket, daemon=True)
		t.start()

	def __energy_func(self, angles, dis, a=6.84091229e+02, b=8.39663324e-02, c=8.91691985e+01, sigma=9.70062189e-03):
		return (a * np.exp(-np.tan(angles - b) ** 2 / sigma) \
        	+ a * np.exp(-np.tan(angles + b) ** 2 / sigma)) / dis ** 2 + c

	def __fit_func(self, vec, quats):
		d = np.linalg.norm(vec)
		vec = vec / d
		radiances = []
		t = time.time()
		for q in quats:
			mat = quat_to_mat(q)
			forward_vec = normalized(mat[1])
			upper_vec = mat[2]
			sgn = np.sign(np.cross(vec, forward_vec).dot(upper_vec))
			angle = np.arccos(forward_vec.dot(vec) * sgn)
			radiances.append(self.__energy_func(angle, d))
		return radiances

	def __residual_func(self, vec, quats, radiances):
		t = time.time()
		val = (np.array(self.__fit_func(vec, quats)) - np.array(radiances)) ** 2
		return val


	def __recv_data_from_socket(self):
		quat_window = Window(WINDOW_SIZE)
		calc_pos_cnt = 0

		while True:	
			quat_buf = conn.recv(2048)
			if not quat_buf:
				break

			# wait for 10 frames of ir radiance for alignment
			# l = len(self.raw_data['radiances'])
			# while len(self.raw_data['radiances']) - l < 10:
			# 	time.sleep(0.001)
			with self.lock:
				ir_radiance = self.serial_window.mean_filter()
				rad_idx = len(self.raw_data['radiances']) - 1


			quats = quat_buf.decode("utf-8").split('\n')[:-1]
			for quat in quats:
				try:
					quat = [float(dim) for dim in quat.split(' ')]
				except:
					print(quat)
					print(quats)
				quat_window.push(quat)

			quat = quat_window.get_last()

			with self.visualizer.lock:
				self.data['quats'].append(quat)
				self.data['radiances'].append(ir_radiance)

			calc_pos_cnt += 1
			if self.energy_func and calc_pos_cnt > 5 and len(self.data['quats']) > PRED_WIN_SIZE:
				calc_pos_cnt = 0
				def runner():
					quats = self.data['quats'][-PRED_WIN_SIZE:]
					radiances = self.data['radiances'][-PRED_WIN_SIZE:]
					# if self.data['vec'] is None:
					# 	vec = quat_to_mat(quats[0])[1]	# initialized as first quat
					# else:
					# 	vec = self.data['vec']
					vec = quat_to_mat(quats[0])[1]
					t = time.time()
					vec = leastsq(self.__residual_func, np.array(vec), maxfev=50, args=(quats, 1023 - np.array(radiances)))[0]
					# print('elapsed time: ', time.time() - t)
					if self.data['vec'] is not None:
						print('Radiance with current vec:', self.__fit_func(self.data['vec'], quats)[0])
					print('radiance: ', 1023 - radiances[0])
					# print('vec: ', vec)
					if math.isnan(vec[0]) or math.isnan(vec[1]) or math.isnan(vec[2]):
						vec = None
					with self.visualizer.lock:
						self.data['vec'] = vec
					self.visualizer.update_data(self.data)
				th = threading.Thread(target=runner)
				th.start()

			# self.visualizer.update_data(self.data)

			self.raw_data['quats'].append([quat, rad_idx])
			self.raw_data['radiances'].append(ir_radiance)


if __name__ == '__main__':
	parser = argparse.ArgumentParser('Server for IR Localization')
	parser.add_argument('-p', '--saved_path')
	args = parser.parse_args()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()

	print("Waiting for connection ...")
	conn, addr = s.accept()
	print("Connected with ", addr)

	server = Server()
	server.start_serial_thread()
	server.start_socket_thread()
	server.visualizer.visualize()

	key = input('PRESS ENTER TO END')

	conn.close()
	server.save_data(args.saved_path)
