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
from scipy.optimize import leastsq
from window import Window
from visualize import Visualizer

HOST = '0.0.0.0'
PORT = 3527
SERIAL_PORT = '/dev/cu.usbmodem142101'
WINDOW_SIZE = 20

class DataCollector():
	def __init__(self):
		self.serial_window = Window(WINDOW_SIZE)
		self.ser = serial.Serial(SERIAL_PORT)
		self.lock = Lock()
		self.data_dict = {'CALI_GYRO': []}
		self.visualizer = Visualizer(self.data_dict)

	def save_data(self, path):
		with open(path, 'wb') as f:
			pickle.dump(self.data_dict, f)

	def start_serial_thread(self):
		t = threading.Thread(target=self.__recv_data_from_serial, daemon=True)
		t.start()

	def __recv_data_from_serial(self):
		while True:
			buf = self.ser.readline().decode()[:-2]	# strip '\r\n'
			self.lock.acquire()
			if buf:
				self.serial_window.push(float(buf))
			self.lock.release()

	def start_socket_thread(self, energy_func):
		t = threading.Thread(target=self.__recv_data_from_socket, daemon=True)
		t.start()

	def __recv_data_from_socket(self, energy_func=None):
		data_window_cali_gyro = Window(WINDOW_SIZE)

		def fit_func(v0, rot_arr):
			d = np.linalg.norm(v0)
			v0_normalized = v0 / d
			theta_arr = np.arccos(np.dot(rot_arr, v0_normalized))
			return 100 * energy_func(theta_arr, d)

		def residual_func(v0, rot_arr, intensity_arr):
			return (fit_func(v0, rot_arr) - intensity_arr) ** 2

		while True:	
			quat_buf = conn.recv(1024)
			if not quat_buf:
				break

			self.lock.acquire()
			ir_intensity = self.serial_window.mean_filter()
			self.lock.release()

			multi_quat_list = quat_buf.decode("utf-8").split('\n')[:-1]		# a list of string, each line contains quaternions from multi sources, separated by ';'
			for multi_quat in multi_quat_list:
				multi_quat = multi_quat.split(';')[:-1]
				multi_quat = [[float(dim) for dim in quat.split(' ')] for quat in multi_quat]	# change quat from str to [float, float, float]
				data_window_cali_gyro.push(multi_quat[0])

			quat_cali_gyro = data_window_cali_gyro.get_last()

			self.data_dict['CALI_GYRO'].append([quat_cali_gyro, ir_intensity])
			self.visualizer.update_data(self.data_dict)
			
			# if energy_func:
			# 	window = data[-WINDOW_SIZE:]
			# 	rot_arr = np.array(x[0] for x in window)		# device's orientation
			# 	intensity_arr = np.array(x[1] for x in window)	# ir intensity
			# 	pos_quat = leastsq(residual_func, v0, args=(rot_arr, intensity_arr))[0]


if __name__ == '__main__':
	parser = argparse.ArgumentParser('Server for IR Localization')
	parser.add_argument('-p', '--saved_path')
	parser.add_argument('-f', '--function', help='file which can be read in as energy function. If None is given, the program will only collect data')
	args = parser.parse_args()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()

	print("Waiting for connection ...")
	conn, addr = s.accept()
	print("Connected with ", addr)

	func = None
	if args.function:
		pass

	collector = DataCollector()
	collector.start_serial_thread()
	collector.start_socket_thread(func)
	collector.visualizer.visualize()

	key = input('PRESS ENTER TO END')

	conn.close()
	collector.save_data(args.saved_path)
