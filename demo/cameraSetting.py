# import v4l2
# vd=open('/dev/video0','rw')
# import v4l2
# import fcntl
# vd = open('/dev/video0', 'rw')
# cp = v4l2.v4l2_capability()
# fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)

# import cv2
# import numpy as np
# video=cv2.VideoCapture(0)
# while True:
#     frame=video.read()
#     cv2.imshow('a',frame)
#     cv2.waitKey(1)
#
# capture.release()
# cv2.destroyAllWindows()

import cv2
import numpy as nmp

capture=cv2.VideoCapture(0)

while True:
    res, frame = capture.read()
    if res:
        cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()