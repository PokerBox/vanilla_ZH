import cv2
import numpy as np
import threading


class SignalViewer(threading.Thread):
    def __init__(self, range=(-1000, 1000), num=1000):
        width = 640
        height = 360
        image = np.ones((height, width, 3), np.uint8)
        image = image * 255
        self.series = []

    def run(self):
        pass

    def add():
        pass
