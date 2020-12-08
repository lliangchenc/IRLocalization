"""Collect raw data for offline usage"""

from socket import *
from IPython import embed
import numpy as np
np.set_printoptions(precision=3)
import threading
import pickle
import argparse
import os
import sys

'''
data format: 
[
	send_direction (tuple), 
	recv_brightness (float), 
	v0_gt (tuple), 
	send_position (tuple)
] or [] (empty list, if grabbing triggered)
'''

buffer = ""
data = []

def recv_data():
	global buffer, data
	while True:
		buf_ = tcpCliSock.recv(8192)
		buffer += buf_.decode("utf-8")
		frames = buffer.split("@")
		buffer = frames[-1]
		for s in frames[:-1]:
			data.append(eval(s))
	
def send_data(s):
	pass

def save_data(filename):
	with open(filename,"wb") as f:
		pickle.dump(data, f)

def load_data(filename="samples.pkl"):
	return pickle.load(open(filename, "rb"))


def data_processing():
	global data
	cnt = 0
	for i in range(len(data)):
		if len(data[i]) == 0:
			cnt += 1
	print(f"flag count: {cnt}")
	for i in range(len(data)):
		if len(data[i]) == 0:
			data = data[(i+1):]
			# print(data[:20])
			print("start flag found!")
			break
	for i in range(len(data)):
		if len(data[i]) == 0:
			data = data[:i]
			# print(data[:20])
			print("end flag found!")
			break

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--port', default=3417, type=int)
	parser.add_argument('--saved_name', default='samples.pkl')
	parser.add_argument('--saved_dir', default='samples')
	args = parser.parse_args()

	if not os.path.exists(args.saved_dir):
		os.mkdir(args.saved_dir)

	s = socket(AF_INET, SOCK_STREAM)
	s.bind(("0.0.0.0", args.port))
	s.listen()

	print("waiting for connection...")
	tcpCliSock, addr = s.accept()
	print("connected from :", tcpCliSock, addr)

	t = threading.Thread(target=recv_data)
	t.daemon = True
	t.start()

	v0 = np.array([1,1,1])

	while True:
		line = sys.stdin.readline()
		break

	print(data)
	data_processing()
	save_data(os.path.join(args.saved_dir, args.saved_name))
