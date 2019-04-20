from YoloDetector import YoloInit, StartYoloDetection
from CVTracker import CVTrackerThread
from VideoProcessor import VideoProcessor
from MultiObjectTracker import MultiObjectTracker
from Connection import SerialThread, RecieveThread
from can.interfaces import slcan

import cv2

YoloInit()

# cap = VideoProcessor('video/filtertest.mp4', fps=10, debug=False, stereo=False)

cap = VideoProcessor(1, fps=30, stereo=False, debug=False)
port = slcan.slcanBus("/dev/ttyACM0", bitrate=1000000)
port.open()

# recvth = RecieveThread(port)
serial = SerialThread(port, None, connect=True, fps=500, debug=True)

Multitracker = MultiObjectTracker(debugMode=False)
# CVTracker = CVTrackerThread(cap, serial, fps=35, debug=False)

cap.start()
# recvth.start()
serial.start()
# CVTracker.start()
StartYoloDetection(cap, Multitracker, None, serial, thresh=0.15, debug=True)
