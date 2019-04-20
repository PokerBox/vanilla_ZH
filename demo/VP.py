from threading import Thread
import time
import cv2
import math
import imutils

class VideoStream():
    def __init__(self, src=1, name="VideoStream"):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.name = name
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            t = time.time()
            if self.stopped:
                return
            (self.grabbed, frame) = self.stream.read()
            # frame = imutils.resize(frame, width=740, height=416)
            frame = cv2.resize(frame, (740, 416), interpolation=cv2.INTER_LINEAR)
            self.frame = imutils.rotate(frame, 180)
            print('FPS: %.2f' % (1.0/(time.time()-t)))

    def read(self):
        return self.grabbed, self.frame

    def stop(self):
        self.stopped = True

if __name__ == '__main__':
    import time
    cap = VideoStream(1)
    cap.start()
    while(True):
        t = time.time()
        _, frame = cap.read()
        # print('FPS: ', 1.0/(time.time()-t))
        cv2.imshow('webcam', frame)
        cv2.waitKey(1)
