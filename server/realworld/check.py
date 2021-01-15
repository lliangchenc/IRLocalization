import numpy as np
import matplotlib.pyplot as plt
import pickle

with open('data/temp.pkl', 'rb') as f:
	data = pickle.load(f)

radiance = np.array(data)[:, 1]
plt.figure()
plt.plot(radiance)
plt.show()
