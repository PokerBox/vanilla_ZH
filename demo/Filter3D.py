from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import time
import numpy as np


class ObjectPredictor():
    def __init__(self, length=[3, 5, 10]):
        self.poly = []
        for i in range(3):
            self.poly.append(PolynomialFeatures(degree=i+1))
        self.regressor1 = LinearRegression()
        self.regressor2 = LinearRegression()
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
        self.preTime = 0.

        T = []
        for i in range(self.length[2]):
            temp = []
            for j in range(i):
                temp.append([j+1])
            print(temp)
            if i+1 < self.length[0]:
                T.append([])
            elif i+1 < self.length[1]:
                temp = self.poly[0].fit_transform(temp)
                T.append(temp)
            elif i+1 < self.length[2]:
                temp = self.poly[1].fit_transform(temp)
                T.append(temp)
            else:
                temp = self.poly[2].fit_transform(temp)
                T.append(temp)

        self.T = T

    def updateSensorAbsolute(self, x, y, yaw, pitch):
        self.yaw = yaw
        self.pitch = pitch
        self.updateSensor(x + yaw, y + pitch)

    def updateSensor(self, x, y):
        self.timestamp = time.time()
        currInterval = self.timestamp - self.preTime
        self.interval = ((self.interval * self.init) + currInterval)/(self.init + 1)
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
                self.regressor1.fit(self.T[self.init-1], self.X[currentLen-self.init:currentLen-1])
                self.regressor2.fit(self.T[self.init-1], self.Y[currentLen-self.init:currentLen-1])
                print("Fit degree-1 regressor.")
                self.degree = 1
            elif self.init < self.length[2]:
                currentLen = len(self.X)
                self.regressor1.fit(self.T[self.init-1], self.X[currentLen-self.init:currentLen-1])
                self.regressor2.fit(self.T[self.init-1], self.Y[currentLen-self.init:currentLen-1])
                print("Fit degree-2 regressor.")
                self.degree = 2
            else:
                del(self.X[0])
                del(self.Y[0])
                currentLen = len(self.X)
                print(self.init)
                self.regressor1.fit(self.T[self.length[2]-1], self.X)
                self.regressor2.fit(self.T[self.length[2]-1], self.Y)
                print("Fit degree-3 regressor.")
                self.degree = 3

    def getPrediction(self, latency=0):
        if self.degree == 0:
            if len(self.X) > 0:
                return self.X[0][len(self.X[0])-1], self.Y[0][len(self.X[0])-1]
            else:
                return 0, 0

        base = self.init 
        if base > self.length[2]:
            base = self.length[2]
        predt = float(base - 1. +
                      (time.time()-self.timestamp)/self.interval + latency)

        predt = self.poly[self.degree-1].fit_transform(np.array([[predt]]))
        print("Predict:\nbase:", base, "\ndegree:", self.degree, "\n", self.T[base-1], "\n", predt)

        predx = self.regressor1.predict(predt)
        predy = self.regressor2.predict(predt)
        print("Predict from degree-%d regressor." % self.degree)
        # except:
        #     currentLen = len(self.X)
        #     self.regressor1.fit(self.T[self.init-1], self.X[currentLen-self.init:currentLen-1])
        #     self.regressor2.fit(self.T[self.init-1], self.Y[currentLen-self.init:currentLen-1])
        #     predx = self.regressor1.predict(predt)
        #     predy = self.regressor2.predict(predt)
        return predx.reshape(-1), predy.reshape(-1)

    def getPredictionAbsolute(self, latency=0):
        x, y = getPrediction(latency)
        return x - self.yaw, y - self.pitch
