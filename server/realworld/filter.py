import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import serial
import pyfirmata
import time

import pyautogui
import numpy as np
from scipy import fftpack, signal

CHUNK = 1024
FFT_LEN = 128
frames = []
SERIAL_PORT = '/dev/cu.usbmodem142101'

class Visualizer():
    def __init__(self):
        board = pyfirmata.Arduino(SERIAL_PORT)
        it = pyfirmata.util.Iterator(board)
        it.start()
        self.analog_input = board.get_pin('a:3:i')

        self.data = []

        self.fig = plt.figure()
        self.stft_ax = plt.subplot()
        f, t, Zxx = signal.stft(np.zeros([1000]), 100, nperseg=40)
        self.stft_plt = self.stft_ax.pcolormesh(t, f, np.abs(Zxx), vmin=0, vmax=5, shading='gouraud')

    def read_ir_thread(self):
        print('i am called')
        while True:
            val = self.analog_input.read()
            if val is not None:
                print(val)
            time.sleep(0.1)


    def visualize(self):
        def plot_init():
            return self.stft_plt,
        
        def plot_update(step):
            f, t, Zxx = signal.stft(self.data[-1000:] * 100, 100, nperseg=40)
            self.stft_plt.set_array(Zxx.ravel())
            return self.stft_plt,

        # ani = animation.FuncAnimation(self.fig, plot_update, init_func=plot_init, frames=1, interval=30, blit=True)
        t = threading.Thread(target=self.read_ir_thread)
        t.start()

        # plt.show()

def main():
    v = Visualizer()
    v.visualize()

if __name__ == '__main__':
    main()
