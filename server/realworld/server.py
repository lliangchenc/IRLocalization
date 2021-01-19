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
from visualize import DataCollectionVisualizer
from utils import *

HOST = '0.0.0.0'
PORT = 3528
SERIAL_PORT = '/dev/cu.usbmodem142101'
WINDOW_SIZE = 10
PRED_WIN_SIZE = 20

class Server():
	def __init__(self, energy_func=None):
		self.serial_window = Window(WINDOW_SIZE)
		self.ser = serial.Serial(SERIAL_PORT)
		self.lock = Lock()
		self.data = {
			'quats': [],
			'radiances': []
		}
		self.visualizer = DataCollectionVisualizer()
		self.raw_data = {
			'quats': [],
			'radiances': []
		}
		self.energy_func = energy_func

	def save_data(self, path):
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
			if buf:
				self.serial_window.push(float(buf))
				self.raw_data['radiances'].append(float(buf))
			self.lock.release()

	def start_socket_thread(self):
		t = threading.Thread(target=self.__recv_data_from_socket, daemon=True)
		t.start()

	def __fit_func(vec, quats):
		d = np.linalg.norm(vec)
		vec = vec / d
		radiances = []
		for q in quats:
			mat = quat_to_mat[0]
			forward_vec = normalized(mat[1])
			upper_vec = mat[2]
			sgn = np.sign(np.cross(vec, vec_forward),dot(vec_upper))
			angle = np.arccos(forward_vec.dot(vec) * sgn)
			radiances.append(self.energy_func(angle, d))
		return radiances

	def __residual_func(vec, quats, radiances):
		return (self.__fit_func(vec, quats) - radiances) ** 2

	def __recv_data_from_socket(self):
		quat_window = Window(WINDOW_SIZE)

		while True:	
			quat_buf = conn.recv(1024)
			if not quat_buf:
				break

			with self.lock:
				ir_radiance = self.serial_window.mean_filter()
				# print('mean: ', ir_radiance)
				rad_idx = len(self.raw_data['radiances']) - 1

			multi_quat_list = quat_buf.decode("utf-8").split('\n')[:-1]		# a list of string, each line contains quaternions from multi sources, separated by ';'
			for multi_quat in multi_quat_list:
				multi_quat = multi_quat.split(';')[:-1]
				multi_quat = [[float(dim) for dim in quat.split(' ')] for quat in multi_quat]	# change quat from str to [float, float, float]
				quat_window.push(multi_quat[0])

			quat = quat_window.get_last()

			with self.visualizer.lock:
				self.data['quats'].append(quat)
				self.data['radiances'].append(ir_radiance)

			if self.energy_func:
				quats = self.data['quats'][-PRED_WIN_SIZE:]
				radiances = self.data['radiances'][-PRED_WIN_SIZE:]
				vec = leastsq(self.__residual_func, vec, args=(quats, radiances))[0]
				with self.visualizer.lock:
					self.data['vec'] = vec

			self.visualizer.update_data(self.data)

			self.raw_data['quats'].append([quat, rad_idx])
			self.raw_data['radiances'].append(ir_radiance)


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

	server = Server()
	server.start_serial_thread()
	server.start_socket_thread()
	server.visualizer.visualize()

	key = input('PRESS ENTER TO END')

	conn.close()
	server.save_data(args.saved_path)
