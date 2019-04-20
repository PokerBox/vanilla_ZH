from KalmanFilter2 import ObjectPredictor
import cv2
import numpy as np
import time
import random

height = 360
width = 640
image = np.ones((height, width, 3), np.uint8)
image = image * 255

obj_x = width/2
obj_y = height/2
speed_x = 10
speed_y = 10
count = 0
period = 30

pred = ObjectPredictor()
count = 0
c = 20

while(True):
    if count % 20 == 0:
        if count % c*5 == 0:
            c = int(random.uniform(20, 20))
            acc_x = random.uniform(-0.5, 0.5)
            acc_y = random.uniform(-0.5, 0.5)

        if obj_x > width or obj_x < 0:
            speed_x = -speed_x
        if obj_y > height or obj_y < 0:
            speed_y = -speed_y

        obj_x = obj_x + speed_x
        obj_y = obj_y + speed_y

        noise_x = random.normalvariate(0, 1)
        noise_y = random.normalvariate(0, 1)

        sensor_x = noise_x + obj_x
        sensor_y = noise_y + obj_y

        speed_x = acc_x + speed_x
        speed_y = acc_y + speed_y

        pred.updateSensor(sensor_x, sensor_y)

    count += 1
    # Draw
    image = np.ones((height, width, 3), np.uint8)
    image = image * 255
    cv2.circle(image, (int(obj_x), int(obj_y)), 8, (255, 0, 0), thickness=5)
    x, y = pred.getPrediction(80)
    cv2.circle(image, (int(x), int(y)), 8, (0, 0, 255), thickness=2)
    # cv2.circle(image, (int(smoother.x[0]), int(
    #     smoother.x[2])), 8, (0, 0, 255), thickness=2)

    cv2.imshow('window', image)
    time.sleep(0.01)
    cv2.waitKey(1)

#TODO degree 1 to 2 