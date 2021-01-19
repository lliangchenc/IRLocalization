import pickle
import numpy as np
from visualize import DataCollectionVisualizer

with open('data/test-0118.pkl', 'rb') as f:
    data = pickle.load(f)
quats = []
radiances = []
for d in data['quats']:
    quat, idx = d
    quats.append(quat)
    radiances.append(data['radiances'][idx])
visualizer = DataCollectionVisualizer()
visualizer.update_data({'quats': quats, 'radiances': radiances})
visualizer.visualize()
