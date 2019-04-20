from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import time
import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter
from scipy.linalg import block_diag


class ObjectPredictor():
    def __init__(self, length=[3, 8]):
        self.poly = []
        for i in range(2):
            self.poly.append(PolynomialFeatures(degree=i+1))
        self.regressor1 = LinearRegression(fit_intercept=False, normalize=False)
        self.regressor2 = LinearRegression(fit_intercept=False, normalize=False)
        self.degree = 0
        self.timestamp = time.time()
        self.X = []
        self.Y = []
        self.init = 0
        self.length = length
        self.ready = False
        self.yaw = 0
        self.pitch = 0
        self.interval = 0.
        self.preTime = time.time()

        T = []

        for i in range(self.length[1]):
            temp = []
            if i+1 < self.length[0]:
                T.append([])
            elif i+1 < self.length[1]:
                for j in range(self.length[0]):
                    temp.append([j])
                temp = self.poly[0].fit_transform(temp)
                T.append(temp)
            else:
                for j in range(self.length[1]):
                    temp.append([j])
                temp = self.poly[1].fit_transform(temp)
                T.append(temp)

        self.T = T
        self.KF = self.newTracker(dt=0.5, var=0.13)
        self.KF_out = self.newTracker(dt=0.5, var=0.13)

    
    def newTracker(self, dt=0.5, var=0.13):
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

    def updateSensorAbsolute(self, x, y, yaw, pitch):
        self.yaw = yaw
        self.pitch = pitch
        self.updateSensor(x + yaw, y + pitch)

    def updateSensor(self, x, y):
        self.KF.update(np.array([x,y]))
        self.KF.predict()
        x, y = self.KF.x[0], self.KF.x[2]
        self.timestamp = time.time()
        currInterval = self.timestamp - self.preTime
        self.interval = ((self.interval * 3) + currInterval)/4
        self.preTime = self.timestamp
        if self.init < self.length[0]:
            self.X.append([x])
            self.Y.append([y])
            self.degree = 0
            self.init += 1
        else:
            self.X.append([x])
            self.Y.append([y])
            self.init += 1
            if self.init < self.length[1]:
                currentLen = len(self.X)
                print(len(self.X), self.init)
                self.regressor1.fit(self.T[self.init-1], self.X[currentLen-self.length[0]:currentLen])
                self.regressor2.fit(self.T[self.init-1], self.Y[currentLen-self.length[0]:currentLen])
                print("Fit degree-1 regressor.")
                self.degree = 1
            else:
                currentLen = len(self.X)
                print(self.init, self.length[1], len(self.X))
                self.regressor1.fit(self.T[self.length[1]-1], self.X)
                self.regressor2.fit(self.T[self.length[1]-1], self.Y)
                print("Fit degree-2 regressor.")
                self.degree = 2
                del(self.X[0])
                del(self.Y[0])
        
    def getPrediction(self, latency=0):
        if self.degree == 0:
            self.KF_out.update(np.array([self.X[self.init-1][0], self.Y[self.init-1][0]]))
            self.KF_out.predict()
            return self.X[self.init-1][0], self.Y[self.init-1][0]

        base = self.init 
        if base > self.length[1]:
            base = self.length[1]
        elif base > self.length[0]:
            base = self.length[0]
        predt = float(base - 1. +
                      (time.time()-self.timestamp)/self.interval + latency)

        predt = self.poly[self.degree-1].fit_transform(np.array([[predt]]))
        print("Predict:\nbase:", base, "\ninteval:", self.interval, "\n", self.T[base-1], "\n", predt)

        predx = self.regressor1.predict(predt)
        predy = self.regressor2.predict(predt)
        print("Predict from degree-%d regressor." % self.degree)
        # except:
        #     currentLen = len(self.X)
        #     self.regressor1.fit(self.T[self.init-1], self.X[currentLen-self.init:currentLen-1])
        #     self.regressor2.fit(self.T[self.init-1], self.Y[currentLen-self.init:currentLen-1])
        #     predx = self.regressor1.predict(predt)
        #     predy = self.regressor2.predict(predt)
        self.KF_out.update(np.array([predx.reshape(-1), predy.reshape(-1)]))
        self.KF_out.predict()
        return self.KF_out.x[0], self.KF_out.x[2]
        # return predx.reshape(-1), predy.reshape(-1)

    def getPredictionAbsolute(self, latency=0):
        x, y = self.getPrediction(latency)
        return x - self.yaw, y - self.pitch
