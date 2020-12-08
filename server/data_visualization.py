"""Visualize the hand position and orientation"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pickle

with open('samples/samples-energy.pkl', 'rb') as f:
	data = pickle.load(f)

X, Y, Z, U, V, W = [], [], [], [], [], []

for frame in data:
	x, y, z = frame[0]
	u, v, w = frame[3]
	X.append(x)
	Y.append(y)
	Z.append(z)
	U.append(u)
	V.append(v)
	W.append(w)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.quiver(X, Y, Z, U, V, W)
ax.set_xlim([-3, 3])
ax.set_ylim([-3, 3])
ax.set_zlim([-3, 3])
plt.show()
