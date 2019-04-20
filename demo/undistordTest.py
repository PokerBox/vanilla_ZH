import cv2
import numpy as np
# cameraMatrix=np.array([[6.029541678562018e+02, 0, 326.456456158280],
#                        [0, 601.295264770454, 220.457310419471],
#                        [0,0,1]])
# cameraDistortion=np.array([-0.429405498060510, 0.192814379459077, 0, 0])
# np.save('/a/123', cameraMatrix)
# np.save('/a/3', cameraDistortion)
cap = cv2.VideoCapture(1)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
while (True):
    _, frame = cap.read()
    # frame=cv2.undistort(frame, cameraMatrix=cameraMatrix, distCoeffs=cameraDistortion)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    centerColumn=frame[:,320,0]
    # for i in range(0,480):
    #     if centerColumn[i]!=0:
    #         cv2.line(frame, (0,i), (639,i), (255,0,0), thickness=1, lineType=8, shift=0)
    #         break
    # for i in range(479,0,-1):
    #     if centerColumn[i]!=0:
    #         cv2.line(frame, (0,i), (639,i), (255,0,0), thickness=1, lineType=8, shift=0)
    #         break
    #
    # frame=frame[62:422, :, :]
    print (cap.get(cv2.CAP_PROP_FPS))
    print(frame.shape)
    cv2.imshow('webcam', frame)