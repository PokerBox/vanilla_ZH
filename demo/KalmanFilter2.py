from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter
from scipy.linalg import block_diag
import numpy as np


class ObjectPredictor():
    def __init__(self, dt=0.75):
        self.filter = self.newTracker(dt=dt)
        self.smoother = self.newTracker(dt=0.3)
        self.predicter = self.newTracker(dt=dt*0.75)
        self.yaw = 0
        self.pitch = 0

    def newTracker(self, dt, var=0.13):
        tracker = KalmanFilter(dim_x=4, dim_z=2)
        tracker.x = np.array([0., 0., 0., 0.])
        tracker.F = np.array([[1, dt, 0,  0],
                              [0,  1, 0,  0],
                              [0,  0, 1, dt],
                              [0,  0, 0,  1]])
        tracker.H = np.array([[1, 0, 0, 0],
                              [0, 0, 1, 0]])
        tracker.P = np.eye(4) * 500.
        tracker.R = np.array([[5., 0.],
                              [0., 5.]])
        tracker.u = 0.
        Q = Q_discrete_white_noise(dim=2, dt=dt, var=var)
        Q = block_diag(Q, Q)
        tracker.Q = Q
        return tracker

    def updateSmoothing(self, latency=0):
        self.filter.predict()
        # self.smoother.predict()
        # self.smoother.update(np.array([self.filter.x[0], self.filter.x[2]]))
        # self.predicter.x = self.smoother.x
        # self.predicter.P = self.smoother.P
        self.predicter.x = self.filter.x
        self.predicter.P = self.filter.P
        for i in range(latency):
            self.predicter.predict()

    def updateSensor(self, x, y):
        data = (x, y)
        self.filter.update(np.array(data))
        # self.updateSmoothing(latency)

    def updateSensorAbsolute(self, x, y, yaw, pitch):
        self.yaw = yaw
        self.pitch = pitch
        self.updateSensor(x + yaw, y + pitch)

    def getPrediction(self, latency=0):
        self.updateSmoothing(latency)
        return self.predicter.x[0], self.predicter.x[2]

    def getPredictionAbsolute(self, latency=0):
        x, y = self.getPrediction(latency)
        return x - self.yaw, y - self.pitch
