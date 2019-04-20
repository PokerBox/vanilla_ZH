from scipy.spatial import distance as dist
from collections import OrderedDict
from CvTracker import CVTrackerThread
import numpy as np


class MultiObjectTracker():
    def __init__(self, cap, maxDisappeared=5):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.maxDisappeared = maxDisappeared
        self.cvthead = None

    def register(self, centroid, rects):
        self.objects[self.nextObjectID] = (centroid, rects)
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1
    
    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]

    def updateCvThread(self):
        if self.objects.__len__ > 0:
            pass

    def update(self, rects):
        changed = False
        if len(rects) == 0:
            for objectID in self.disappeared.keys():
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
                    changed = True

        inputCentroids = np.zeros((len(rects), 2), dtype="int")

        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i], rects[i])
            if changed:
                self.updateCvThread()
            return self.objects
        else:
            objectIDs = list(self.objects.keys())
            objectPair = list(self.objects.values())

            D = dist.cdist(np.array(objectPair[0]), inputCentroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()
 
            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue

                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0

                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            
            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)
                        changed = True
            else:
                for col in unusedCols:
                    self.register([col], )
                changed = True
            
            if changed:
                self.updateCvThread()

        return self.objects