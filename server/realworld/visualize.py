import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
import threading
import numpy as np
from IPython import embed
from utils import *
from enum import Enum


class PlotterType(Enum):
	IR_RADIANCE = 1
	ENERGY_FUNC = 2
	LOCATION = 3


class Position():
	def __init__(self, x=0, y=0):
		self.set(x, y)
	def set(self, x, y):
		self.x = x
		self.y = y
	def __str__(self):
		return f'x: {self.x}, y: {self.y}'


class IrRadiancePlotter():
	def __init__(self, ax):
		self.ax = ax
		self.ax.set_xlim(0, 1000)
		self.ax.set_ylim(0, 1200)
		self.ax.set_title('IR Radiance')
		self.radiances = []
		self.plot, = plt.plot([], [])

	def update_data(self, radiances=None):
		if radiances:
			self.radiances = radiances

	def update_plot(self):
		self.plot.set_xdata(np.arange(0, len(self.radiances)))
		self.plot.set_ydata(self.radiances)
		return self.plot


class EnergyFuncPlotter():
	def __init__(self, ax):
		self.ax = ax
		self.ax.set_xlim(-60, 60)
		self.ax.set_ylim(0, 1200)
		self.ax.set_title('Energy Function')
		self.quats = []
		self.radiances = []
		self.scatter = self.ax.scatter([], [], s=5.0)
		self.lock = threading.Lock()

	def quats_to_angles(self, quats):
		angles = []
		if len(quats) == 0:
			return []
		vec_origin = normalized(quat_to_mat(quats[0])[1])
		for q in quats:
			if q == quats[0]:
				angles.append(0)
				continue
			mat = quat_to_mat(q)
			vec_forward = normalized(mat[1])
			vec_upper = mat[2]
			sgn = np.sign(np.cross(vec_origin, vec_forward).dot(vec_upper))
			angles.append(np.arccos(vec_forward.dot(vec_origin)) * sgn)
		return np.degrees(angles)

	def update_data(self, quats=None, radiances=None):
		self.quats = quats
		self.radiances = radiances

	def update_plot(self):
		self.scatter.set_offsets(np.array([self.quats_to_angles(self.quats), self.radiances]).T)
		return self.scatter


class LocationPlotter():
	def __init__(self, ax):
		self.ax = ax
		self.ax.set_xlim(-2, 2)
		self.ax.set_ylim(0, 5)
		self.ax.set_title('Sender Location')
		self.recv_pos = Position(0, 0)
		self.send_pos = Position()
		self.scatter = self.ax.scatter([self.recv_pos.x], [self.recv_pos.y])

	def update_data(self, vec):
		x, y, z = vec
		self.send_pos.set(x, y)

	def update_plot(self):
		self.scatter.set_offsets([[self.recv_pos.x, self.recv_pos.y], [self.send_pos.x, self.send_pos.y]])
		return self.scatter


class Visualizer():
	def __init__(self):
		self.fig = plt.figure()
		self.plotters = dict()
		self.lock = threading.Lock()

	def update_data(self, data):
		with self.lock:
			for ptype in self.plotters:
				plotter = self.plotters[ptype]
				if ptype == PlotterType.IR_RADIANCE:
					plotter.update_data(data['radiances'])
				elif ptype == PlotterType.ENERGY_FUNC:
					plotter.update_data(data['quats'], data['radiances'])
				elif ptype == PlotterType.LOCATION:
					plotter.update_data(data['vec'])

	def update_plots(self, step):
		plots = []
		with self.lock:
			for ptype in self.plotters:
				plots.append(self.plotters[ptype].update_plot())
		return plots

	def visualize(self):
		ani = animation.FuncAnimation(self.fig, self.update_plots, frames=1, interval=30, blit=True)
		plt.show()


class DataCollectionVisualizer(Visualizer):
	def __init__(self):
		super().__init__()
		# ir_radiance_ax = plt.subplot(211)
		# energy_func_ax = plt.subplot(212)
		# self.plotters[PlotterType.IR_RADIANCE] = IrRadiancePlotter(ir_radiance_ax)
		# self.plotters[PlotterType.ENERGY_FUNC] = EnergyFuncPlotter(energy_func_ax)
		energy_func_ax = plt.subplot()
		self.plotters[PlotterType.ENERGY_FUNC] = EnergyFuncPlotter(energy_func_ax)


class LocalizationVisualizer(Visualizer):
	def __init__(self):
		super().__init__()
		ir_radiance_ax = plt.subplot(211)
		location_ax = plt.subplot(212)
		self.plotters[PlotterType.IR_RADIANCE] = IrRadiancePlotter(ir_radiance_ax)
		self.plotters[PlotterType.LOCATION] = LocationPlotter(location_ax)
