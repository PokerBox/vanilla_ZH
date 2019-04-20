from scipy.spatial import distance as dist
from collections import OrderedDict  # why OrderedDict?
import numpy as np
import cv2
import datetime
import pprint
import os


class MultiObjectTracker():
    '''
    Keep track of multiple objects and match detection results to corresponding objects.
    :param cap: A reference to the VideoProcessor (i.e. cvThread) to get current frame
    :param maxDisappeared: max number of times an object can miss from detection results before being removed
    :param maxMatchDistance: max distance between two bounding boxes that can be considered belonging to one object
    :param maxIgnoreDistance: max distance that all passed-in bboxes in this range are considered one bbox
    :param minAppearance: min time an object needs to appear before adding to the valid object list
    :param isCVTrackerOn: Just keep it false
    :param cvTrackerType: method used for CV trackers
    :param debugMode: if true, program will output a logfile to the current directory
    '''
    availableTrackerTypes = {'TLD': 'TrackerTLD_create',
                             'MEDIANFLOW': 'TrackerMedianFlow_create',
                             'CSRT': 'TrackerCSRT_create'}

    def __init__(self, maxDisappeared=1, maxMatchDistance=15, maxIgnoreDistance=8, minAppearance=3, isCVTrackerOn=False, cvTrackerType='MEDIANFLOW', debugMode=True):
        assert cvTrackerType in MultiObjectTracker.availableTrackerTypes, 'cvTrackerType not in availableTrackerTypes'
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.validObjects = OrderedDict()
        # TODO: Add depth to objects
        self.disappeared = OrderedDict()
        self.maxDisappeared = maxDisappeared
        self.maxMatchDistance = maxMatchDistance
        self.maxIgnoreDistance = maxIgnoreDistance
        self.minAppearance = minAppearance
        self.isCVTrackerOn = isCVTrackerOn
        if isCVTrackerOn:
            self.cvTrackers = {}
        self.trackerFunctionName = MultiObjectTracker.availableTrackerTypes[cvTrackerType]
        self.debugMode = debugMode
        if debugMode:
            if not os.path.exists('Logs'):
                os.makedirs('Logs')
            fileName = 'Logs/MOTLog_' + \
                str(datetime.datetime.now().time()).replace(':', '.')+'.txt'
            self.logFile = open(fileName, 'w+')
            self.updateTimes = 1
            self.pp = pprint.PrettyPrinter(indent=4, stream=self.logFile)

    def updateObject(self, centroid, rects, label, frame=None, objectID=-1):
        '''
        Update an object's information, and create one if objectID is not given (or -1)
        :param centroid: an 1x2 array [x,y] indicating the center of the bounding box
        :param rects: bounding box in the format of a tuple (startX, startY, endX, endY)
        :param label: classified label
        :param objectID: optional. If given, update corresponding object information, otherwise, create new object
        '''
        counter = 1
        if (objectID == -1):
            # No objectID given, create a new id for it
            objectID = self.nextObjectID
            self.nextObjectID += 1
            if self.isCVTrackerOn:
                # Initialize cv tracker
                self.cvTrackers[objectID] = getattr(
                    cv2, self.trackerFunctionName)
        else:
            counter = self.objects[objectID][3]+1
        if self.isCVTrackerOn:
            # NOTE: opencv bbox format: (xmin,ymin,boxwidth,boxheight)
            bbox = (rects[0], rects[1], rects[2] -
                    rects[0], rects[3] - rects[1])
            self.cvTrackers[objectID].init(frame, bbox)
        self.objects[objectID] = (centroid, rects, label, counter)
        if counter > self.minAppearance:
            self.validObjects[objectID] = (centroid, rects, label, counter)
            self.disappeared[objectID] = 0

    def updateDisappeared(self, frame, objectID):
        '''
        Update 'disappeared' information of a given object, remove if it has been missed for more than 'maxDisappeared' times
        :param objectID: objectID
        :param frame: current frame of video input
        '''
        if self.objects[objectID][3] <= self.minAppearance:
            self.deregister(objectID, False)
            return
        if objectID in self.disappeared:
            self.disappeared[objectID] += 1
            if self.disappeared[objectID] > self.maxDisappeared:
                self.deregister(objectID, True)
                return
        else:
            self.disappeared[objectID] = 1
        if self.isCVTrackerOn:
            # Use cv trackers to update objects that are not detected by yolo
            ok, bbox = self.cvTrackers[objectID].update(frame)
            if ok:
                endX = bbox[0] + bbox[2]
                endY = bbox[1] + bbox[3]
                cX = int((bbox[0] + endX) / 2.0)
                cY = int((bbox[1] + endY) / 2.0)
                _, _, label = self.objects[objectID]
                self.objects[objectID] = (
                    (cX, cY), (bbox[0], bbox[1], endX, endY), label)
            else:
                print(
                    'Error in MultiObjectTracker.updateDisappeared: cvTracker update failed')

    def deregister(self, objectID, moveFromValidObjects):
        del self.objects[objectID]
        if moveFromValidObjects:
            del self.disappeared[objectID]
            del self.validObjects[objectID]
        if self.isCVTrackerOn:
            del self.cvTrackers[objectID]

    def updateCvThread(self):
        if self.objects.__len__ > 0:
            pass

    def getObjects(self):
        return self.objects

    def xywhToMinmax(self, bbox):
        return (bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3])

    def update(self, rects):
        '''
        Update object lists and match detection results to objects. Return objects at the end.
        :param rects: A list of lists containing bounding box as a tuple of (startX, startY, endX, endY) and the detected object label
        '''
        # [(label,conf,bbox)]

        if self.debugMode:
            self.logFile.write('=========Update ' +
                               str(self.updateTimes)+'===========\n')
            self.updateTimes += 1
            self.logFile.write('* Passed in values:\n')
            self.pp.pprint(rects)
            self.logFile.write(('\n* Current objects: \n'))
            self.pp.pprint(self.objects)
            self.logFile.write(('\n* Current validObjects: \n'))
            self.pp.pprint(self.validObjects)
            self.logFile.write(('\n* Current disappeared: \n'))
            self.pp.pprint(self.disappeared)
        # if self.isCVTrackerOn:
        #     pass
        #     # frame=self.cvThread.frame
        # else:
        frame = None

        # Change the format of the rects
        rectsOld = rects
        rects = []
        for item in rectsOld:
            label, _, bbox = item
            if label == 'Robot':
                continue
            rects.append([self.xywhToMinmax(bbox), label])
        # No object detected
        if (len(rects) == 0):
            for objectID in self.objects:
                self.updateDisappeared(frame, objectID)
            return
        # Initialize centroids, labels, and objects
        labels = []
        inputCentroids = np.zeros((len(rects), 2), dtype='int')
        currentObjectIDs = list(self.objects.keys())
        currentObjectInfo = list(self.objects.values())
        for (i, ((startX, startY, endX, endY), label)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
            labels.append(label)

        newRects = []
        newCentroids = []
        #newCentroids=np.zeros((len(rects), 2), dtype='int')
        skipList = []
        addedList = []

        # currentI=0
        # while (currentI<len(rects)):
        #     numToRemove=[]
        #     currentCentroid=inputCentroids[currentI]
        #     for i in range(currentI+1,len(rects)):
        #         deltaX=currentCentroid[0]-inputCentroids[i][0]
        #         deltaY=currentCentroid[1]-inputCentroids[i][1]
        #         distance=(deltaX*deltaX+deltaY*deltaY)**(1/2.0)
        #         if distance<self.maxIgnoreDistance:
        #             numToRemove.append(i)
        #     for removeIndex in numToRemove:
        #         del rects[removeIndex]
        #         del inputCentroids[removeIndex]
        #     currentI+=1
        # print (inputCentroids)
        for i in range(0, len(inputCentroids)):
            if i in skipList:
                continue
            for j in range(0, len(inputCentroids)):
                # print(newCentroids)
                distance = dist.cdist(
                    np.array([inputCentroids[i]]), np.array([inputCentroids[j]]))
                #print(inputCentroids[i], inputCentroids[j], distance, end=' ')
                if i == j and i not in addedList:
                    newRects.append(rects[i])
                    newCentroids.append(inputCentroids[i])
                    addedList.append(i)
                elif (j in skipList):
                    continue
                elif distance < self.maxIgnoreDistance:
                    skipList.append(j)
                else:
                    if i not in addedList:
                        newRects.append(rects[i])
                        newCentroids.append(inputCentroids[i])
                        addedList.append(i)
        rects = newRects
        # inputCentroids=newCentroids
        inputCentroids = np.asarray(newCentroids, dtype='int')

        # TODO: figure out a way to find best match instead of closest match
        # Remove unnecessary calculation for distance to improve performance

        # Update current objects
        # Track if one bbox has been matched
        matchedResult = np.ones((len(inputCentroids), 1), dtype='int').dot(-1)
        for i in range(len(currentObjectIDs)):
            hasUpdated = False
            currentCentroid, currentRects, currentLabel, _ = currentObjectInfo[i]
            currentID = currentObjectIDs[i]
            # print (inputCentroids)
            D = dist.cdist(np.array([currentCentroid]), inputCentroids)
            sortedArgs = D.min(axis=0).argsort()
            if self.debugMode:
                self.logFile.write('\n ### Comparing '+str(currentID) +
                                   ': current object info (CRLC) ' + str(currentObjectInfo[i])+'\n')
                self.logFile.write('\n* currentCentroid:\n')
                self.pp.pprint(currentCentroid)
                self.logFile.write('\n* inputCentroids:\n')
                self.pp.pprint(inputCentroids)
                self.logFile.write('\n* D:\n')
                self.pp.pprint(D)
                self.logFile.write('\n* sortedArgs:\n')
                self.pp.pprint(sortedArgs)
            for pos in range(0, len(sortedArgs)):
                if (sortedArgs[pos] > self.maxMatchDistance):
                # if (D[sortedArgs[pos]] > self.maxMatchDistance):
                    break
                # labels[pos]!=currentLabel or
                elif (matchedResult[sortedArgs[pos]] != -1):
                    continue
                else:
                    matchedResult[sortedArgs[pos]] = i
                    # print(i, len(rects))
                    #self.updateObject(inputCentroids[pos], rects[i][0], currentLabel, frame, currentID)
                    self.updateObject(
                        inputCentroids[sortedArgs[pos]], rects[sortedArgs[pos]][0], currentLabel, frame, currentID)
                    hasUpdated = True
                    break
            # Update disappeared if no centroid matched to this object
            if not hasUpdated:
                self.updateDisappeared(frame, currentID)
                # hasUpdated=True
        # Add newly detected objects to 'self.objects', if they are not matched to any existing object
        for i in range(0, len(matchedResult)):
            if matchedResult[i] == -1:
                currentRects, currentLabel = rects[i]
                self.updateObject(
                    inputCentroids[i], currentRects, currentLabel, frame)
