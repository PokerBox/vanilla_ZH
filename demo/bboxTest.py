import numpy as np
import cv2
import sys
from BBoxPreprocessor import process
from matplotlib import pyplot as plt
class Object_Tracking:
    available_match_method=['NCC','SIFT']
    def __init__(self):
        #self.object_template=object_template
        self.video=cv2.VideoCapture(1)
        # if not self.video.isOpened():
        #     print("Could not open video")
        #     sys.exit()
        self.rects=[['Blue',0.9,(320,320,100,80)]]


    def tracking(self):
        while True:
            is_device_ready, frame=self.video.read()
            if not is_device_ready:
                break

            # Start timer
            timer = cv2.getTickCount()

            # Find match
            process(self.rects,currentFrame=frame,debugMode=True)

            # Calculate Frames per second (FPS)
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

            # Display FPS on frame
            cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

            #Display bounding box
            # Tracking success
            bbox=self.rects[0][2]
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            # Display result
            cv2.imshow("Tracking", frame)

            # Exit if ESC pressed
            k = cv2.waitKey(1) & 0xff
            if k == 27: break

ot=Object_Tracking()
ot.tracking()
