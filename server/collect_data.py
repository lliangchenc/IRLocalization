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
import time

'''
data format: 
[
	src_direction (tuple), 
	src_position (tuple),
	recv1_brightness (float), recv1_v0_gt (tuple), 
	...
] or 
[] (empty list, if grabbing triggered) or 
[distance, length]
'''

buffer = ""
data = []
mutex = threading.Lock()

def recv_data():
	global buffer, data
	while True:
		buf_ = tcpCliSock.recv(8192)
		buffer += buf_.decode("utf-8")
		frames = buffer.split("@")
		buffer = frames[-1]
		mutex.acquire()
		for s in frames[:-1]:
			data.append(eval(s))
		mutex.release()
	
def send_data(s):
	pass

def save_data(filename):
	with open(filename,"wb") as f:
		pickle.dump(data, f)

def load_data(filename="samples.pkl"):
	return pickle.load(open(filename, "rb"))


def trimData():
	"""
	trim the data out of the empty frame; used in energy function fitting
	"""
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
	parser.add_argument('--saved_name', default='samples')
	parser.add_argument('--saved_dir', default='samples')
	parser.add_argument('--fit', action='store_true')
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

	onDataTransferFlag = False	# True if data transfer is on
	distance = None
	length = None

	idx = 0

	while True:
		if len(data) == idx:		# no frame is received
			if onDataTransferFlag:	# data transfer is off; save data which is named with current config
				onDataTransferFlag = False
				mutex.acquire()
				if args.fit:
					trimData()
				filename = os.path.join(args.saved_dir, f"{args.saved_name}_d_{distance}_l_{length}.pkl")
				save_data(filename)
				print(f"Data saved in file: {filename}")
				data.clear()
				mutex.release()
				idx = 0
		else:
			idx = len(data)
			if not onDataTransferFlag:	# start data transfer with a new config; save the config
				onDataTransferFlag = True
				config_frame = data[0]
				distance = config_frame[0]
				length = config_frame[1]
				mutex.acquire()
				data = data[1:] # trim the config frame
				mutex.release()
				print(f"Current scene config: distance {distance} m, length: {length} m")
		time.sleep(0.1)	# sleep for a short period to make sure at least one frame is received when data transfer is on.
