import numpy as np

class Window():
    def __init__(self, size):
        self.window = []
        self.size = size

    def is_full(self):
        return len(self.window) == self.size

    def pop(self):
        self.window = self.window[:-1]

    def push(self, item):
        if self.is_full():
            self.pop()
        self.window.append(item)

    def concat(self, items):
        self.window += items
        self.window = self.window[-20:]

    def get_last(self):
        return self.window[-1]
    
    def mean_filter(self):
        return np.mean(self.window)
