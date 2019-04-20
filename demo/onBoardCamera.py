import cv2
import numpy as np
#2592x1944 FR=30
#2592x1458 FR=30
#1280x720  FR=120
imageWidth=1280
imageHeight=720
frameRate=120
onboardCamera="nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)"+imageWidth+", height=(int)"+imageHeight+", format=(string)I420, framerate=(fraction)"+frameRate+"/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
video=cv2.VideoCapture(onboardCamera)

while True:
    r,frame=video.read()
    cv2.imshow('a',frame)
    cv2.waitKey(1)
