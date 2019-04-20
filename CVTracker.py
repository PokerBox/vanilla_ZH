import time
import cv2
import math
import threading
from random import randint


class CVTrackerThread(threading.Thread):
    def __init__(self, cap, serial, trackerType='MEDIANFLOW', fps=120, debug=False):
        super(CVTrackerThread, self).__init__()
        self.cap = cap
        self.filter = serial.filter
        self.serial = serial

        self.trackerTypes = ['TLD', 'MEDIANFLOW', 'CSRT']
        self.tracker = None
        self.type = trackerType

        self.initTracker = False
        self.NNframe = False
        self.stop = True

        self.fps = fps
        self.debug = debug
        self.bbox = []
        self.frame = None

    def createTrackerByName(self, trackerType):
        if trackerType == self.trackerTypes[0]:
            tracker = cv2.TrackerTLD_create()
        elif trackerType == self.trackerTypes[1]:
            tracker = cv2.TrackerMedianFlow_create()
        elif trackerType == self.trackerTypes[2]:
            tracker = cv2.TrackerCSRT_create()
        else:
            tracker = None
        return tracker

    def update(self, frame):
        status, self.bbox = self.tracker.update(frame)
        if not status:
            self.serial.validate = False
            self.clear()

    def init(self, bbox):
        self.bbox = bbox
        self.initTracker = True
    
    def updateByNN(self, frame, bbox):
        self.bbox = bbox
        self.frame = frame
        self.stop = False
        self.NNframe = True

    def sendToFilter(self):
        xmin, ymin, w, h = self.bbox
        pix_x = float(xmin + w/2)
        pix_y = float(ymin + h/2)
        x = math.atan((pix_x - 740./2) / 693.3) * 1800 / math.pi
        y = math.atan((pix_y - 416./2) / 693.3) * 1800 / math.pi
        # self.filter.updateSensorAbsolute(x, 0, self.serial.yaw, 0)
        self.serial.x = int(x)
        self.serial.y = int(y)

    def clear(self):
        self.stop = True
        self.serial.validate = False
    
    def restart(self):
        self.stop = False

    def run(self):
        while True:
            if self.stop:
                self.tracker = None
                if self.debug:
                    print('- CVTracker Stopped')
                time.sleep(0.01)
                continue

            prevTime = time.time()
            _, frame = self.cap.read()
            if self.initTracker:
                self.tracker = self.createTrackerByName(self.type)
                self.tracker.init(frame, self.bbox)
                if self.debug:
                    print('- CVTracker Initialized')
                self.initTracker = False
            elif self.NNframe:
                if self.tracker == None:
                    self.tracker = self.createTrackerByName(self.type)
                    if self.debug:
                        print('- CVTracker Created')
                self.tracker.init(self.frame, self.bbox)
                self.update(frame)
                self.sendToFilter()
                if self.debug:
                    print('- CVTracker Updated By Neural Network')
                self.NNframe = False
            elif self.tracker != None:
                self.update(frame)
                if self.debug:
                    print('- CVTracker Computed')
                    print(self.bbox)
                self.sendToFilter()

            currentTime = time.time()
            runTime = currentTime - prevTime
            waitTime = 1./self.fps - runTime
            if self.debug:
                print('- CVTracker FPS: %.2f' % (1.0/runTime))
            if(waitTime > 0):
                time.sleep(waitTime)

# TEST
if __name__ == '__main__':
    from Connection import SerialThread
    cap = cv2.VideoCapture(0)
    serial = SerialThread(connect=False, fps=120, debug=False)
    serial.start()
    cvthread = CVTrackerThread(cap, serial, fps=120, debug=True)
    cvthread.start()
    _, frame = cap.read()
    bbox = cv2.selectROI('Draw BBOX', frame, fromCenter=False)
    cvthread.init(bbox)
    for i in range(8):
        time.sleep(1)
    _, frame = cap.read()
    bbox = cv2.selectROI('Draw BBOX', frame, fromCenter=False)
    cvthread.updateByNN(frame, bbox)



# (291, 223, 80, 44), (123, 239, 65, 56)
