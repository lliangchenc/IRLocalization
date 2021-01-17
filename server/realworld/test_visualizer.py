import matplotlib.pyplot as plt
from visualize import *
import threading
from time import sleep

class RadianceVisualizer(Visualizer):
    def __init__(self):
        super().__init__()
        ax = plt.subplot(111)
        self.plotters[PlotterType.IR_RADIANCE] = IrRadiancePlotter(ax)

class EnergyFuncVisualizer(Visualizer):
    def __init__(self):
        super().__init__()
        ax = plt.subplot(111)
        self.plotters[PlotterType.ENERGY_FUNC] = EnergyFuncPlotter(ax)

class LocationVisualizer(Visualizer):
    def __init__(self):
        super().__init__()
        ax = plt.subplot(111)
        self.plotters[PlotterType.LOCATION] = LocationPlotter(ax)

class VisualizerTester():
    def __init__(self):
        self.visualizer = None
        self.stop_thread_flag = False
        self.init_data = {
            'quats': [[1, 0, 0, 0]],
            'radiances': [10],
            'vec': [0, 1, 0],
            'dis': 0
        }
        self.data = self.init_data

    def radiance_test(self):
        self.visualizer = RadianceVisualizer()
        self.test()
    
    def energy_func_test(self):
        self.visualizer = EnergyFuncVisualizer()
        self.test()

    def location_test(self):
        self.visualizer = LocationVisualizer()
        self.test()

    def feed_data(self):
        while not self.stop_thread_flag:
            self.data['quats'].append(self.data['quats'][-1])
            self.data['radiances'].append(self.data['radiances'][-1] + 10)
            self.data['dis'] = self.data['dis'] + 0.005
            self.visualizer.update_data(self.data)
            sleep(0.1)

    def test(self):
        self.data = self.init_data
        self.stop_thread_flag = False
        t = threading.Thread(target=self.feed_data)
        t.start()
        self.visualizer.visualize()
        self.stop_thread_flag = True

if __name__ == '__main__':
    tester = VisualizerTester()
    print('Testing radiance ...')
    tester.radiance_test()
    print('Testing energy function ...')
    tester.energy_func_test()
    print('Testing location ...')
    tester.location_test()
