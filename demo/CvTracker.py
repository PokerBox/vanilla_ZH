import time
import cv2
import threading
from random import randint


class CVTrackerThread(threading.Thread):
    def __init__(self, cap, bboxes, trackerType='TLD', debug=False, resolution=None):
        super(CVTrackerThread, self).__init__()
        self.detector = []
        self.colors = []
        self.cap = cap
        self.resolution = resolution
        self.trackerTypes = ['TLD', 'MEDIANFLOW', 'CSRT']
        self.debug = debug
        for bbox in bboxes:
            if debug:
                self.colors.append(
                    (randint(0, 255), randint(0, 255), randint(0, 255)))
            self.detector.append(
                (self.createTrackerByName(trackerType), bbox, True))

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

    def add(self, bbox, trackerType='TLD'):
        self.detector.append((self.createTrackerByName(trackerType), bbox, True))
    
    def remove(self):
        pass

    def update(self, frame):
        for i in range(len(self.detector)):
            self.detector[i][2], self.detector[i][1] = self.detector[i][0].update(
                frame)

    def run(self):
        while self.cap.isOpened():
            prev_time = time.time()
            frame = self.cap.read()

            if self.resolution != None:
                frame = cv2.resize(
                    frame, self.resolution, interpolation=cv2.INTER_LINEAR)

            if self.debug:
                print("CVTracker FPS: %.2f" % (1.0/(time.time()-prev_time)))
                print()


# TEST
if __name__ == '__main__':
    from VideoProcessor import VideoProcessor
    cap = VideoProcessor(0)
    cap.start()
    thread = CVTrackerThread(cap, (), debug=True)
    thread.start()
    while(True):
        print(thread.bboxes)
        time.sleep(1)


# (291, 223, 80, 44), (123, 239, 65, 56)
