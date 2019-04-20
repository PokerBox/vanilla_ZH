import numpy as np
import cv2

#large img
left_camera_matrix=np.array([[832.435658123356,0.,679.097692053230],
                             [0.,834.154701860582,520.052455316846],
                             [0.,0.,1]])
left_distortion=np.array([-0.377556841877811,0.119187796731564,0.000244059708238597,0.000942934866738105])

right_camera_matrix=np.array([[831.698786244524,0.,673.352686245399],
                              [0,836.533841311744,519.093704144343],
                              [0.,0.,1]])
right_distortion=np.array([-0.346760277995920,0.0848078234665875,0.00159692034796570,-0,0.0000622650672924687])
R=np.array([[0.999642944780343,0.00110588320819119,-0.0266975649304055],
[-0.00120272633595674,0.999992754766322,-0.00361162902620857],
[0.0266933774604147,0.00364244933966102,0.999637032208473]])
R=np.transpose(R)
T=np.array([-5.93877302419152,-0.0259699410014745,0.245447082761350])
img_size=(1280,960)

R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(left_camera_matrix, left_distortion,
                                                                  right_camera_matrix, right_distortion, img_size, R,
                                                                  T,alpha=0.5)
left_map1, left_map2 = cv2.initUndistortRectifyMap(left_camera_matrix, left_distortion, R1, P1, img_size, cv2.CV_16SC2)
right_map1, right_map2 = cv2.initUndistortRectifyMap(right_camera_matrix, right_distortion, R2, P2, img_size, cv2.CV_16SC2)

#---------------------

cv2.namedWindow("left")
cv2.namedWindow("right")
cv2.moveWindow("left", 0, 0)
cv2.moveWindow("right", 600, 0)
cv2.createTrackbar("num", "depth", 0, 10, lambda x: None)
cv2.createTrackbar("blockSize", "depth", 5, 255, lambda x: None)
camera=cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,960)

img_width=1280
point1=(0,100)
point2=(1248,802)

excludedItems=[-9652,np.inf,-np.inf]
blankElement=np.array([0,0,0])
while True:
    is_ok, frame=camera.read()
    if not is_ok:
        break
    frame1=frame[:,0:img_width]
    frame2 = frame[:, img_width:]

    # 根据更正map对图片进行重构
    img1_rectified = cv2.remap(frame1, left_map1, left_map2, cv2.INTER_LINEAR)
    img2_rectified = cv2.remap(frame2, right_map1, right_map2, cv2.INTER_LINEAR)

    img1_rectified = img1_rectified[point1[1]:point2[1], point1[0]:point2[0], :]
    img2_rectified = img2_rectified[point1[1]:point2[1], point1[0]:point2[0], :]
    print(img1_rectified.shape,img2_rectified.shape)

    cv2.imshow("left", img1_rectified)
    cv2.imshow("right", img2_rectified)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()