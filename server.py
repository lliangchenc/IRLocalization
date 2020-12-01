from socket import *
from IPython import embed
import numpy as np
np.set_printoptions(precision=3)
import threading
import pickle

from scipy.optimize import leastsq

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

def energy_func(theta, d, sigma=0.2):
	return 1.0 / sigma * np.exp(- np.tan(theta) ** 2 / sigma ** 2) / d ** 2
	
def fit_func(v0, vi_array):
	d = np.linalg.norm(v0)
	v0_normalized = v0 / d
	theta_arr = np.arccos(np.dot(vi_array, v0_normalized))
	return 100 * energy_func(theta_arr, d)

def residual_func(v0, vi_array, sig_array):
    return (fit_func(v0, vi_array) - sig_array)**2
	
def save_data(filename="samples.pkl"):
	with open("samples.pkl","wb") as f:
		pickle.dump(data, f)
		f.close()

def load_data(filename="samples.pkl"):
	return pickle.load(open(filename, "rb"))
	
s = socket(AF_INET, SOCK_STREAM)
s.bind(("0.0.0.0",3417))
s.listen()

print("waiting for connection...")
tcpCliSock, addr = s.accept()
print("connected from :", tcpCliSock, addr)

t = threading.Thread(target=recv_data)
t.daemon = True
t.start()

v0 = np.array([1,1,1])

while True:
	#if len(data) > 0:
	#	print(data[-1])
	if len(data) > 10000:
		save_data()
		data = data[-9000:]
		
	if len(data) < 20:
		continue
	frames = data[::2][-20:]
	vi_array = np.array([x[0] for x in frames])
	sig_array = np.array([x[1] for x in frames])
	v0_gt = np.mean(np.array([x[2] for x in frames]), axis=0)
	v0 = leastsq(residual_func, v0, args=(vi_array,sig_array))[0]
	d = np.linalg.norm(v0)
	if d > 1e3 or np.isnan(d):
		v0 = np.array([1,1,1])
	print(v0, v0_gt)
	tcpCliSock.send(( str([float('{:.3f}'.format(x)) for x in v0])+"@").encode())

embed()