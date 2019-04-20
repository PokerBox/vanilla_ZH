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
cv2.namedWindow("depth")
cv2.moveWindow("left", 0, 0)
cv2.moveWindow("right", 600, 0)
cv2.createTrackbar("num", "depth", 0, 10, lambda x: None)
cv2.createTrackbar("blockSize", "depth", 5, 255, lambda x: None)
camera=cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,960)
# 添加点击事件，打印当前点的距离
def callbackFunc(e, x, y, f, p):
    if e == cv2.EVENT_LBUTTONDOWN:
        print (threeD[y][x])

cv2.setMouseCallback("depth", callbackFunc, None)
img_width=1280
# point1=(150,110)
# point2=(170,130)
point1=(0,33)
point2=(1248,735)

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
    # 将图片置为灰度图，为StereoBM作准备
    imgL = cv2.cvtColor(img1_rectified, cv2.COLOR_BGR2GRAY)
    imgR = cv2.cvtColor(img2_rectified, cv2.COLOR_BGR2GRAY)

    # 两个trackbar用来调节不同的参数查看效果
    num = cv2.getTrackbarPos("num", "depth")+1
    blockSize = cv2.getTrackbarPos("blockSize", "depth")
    if blockSize % 2 == 0:
        blockSize += 1
    if blockSize < 5:
        blockSize = 5

    #stereo = cv2.StereoSGBM_create(minDisparity=1, numDisparities=32, blockSize=blockSize)
    stereo = cv2.StereoSGBM_create(numDisparities=16*num, blockSize=blockSize)
    disparity = stereo.compute(imgL, imgR)

    disp = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    threeD = cv2.reprojectImageTo3D(disparity.astype(np.float32)/16.,Q)
    cv2.rectangle(disp,point1,point2,color=255)

    cv2.imshow("left", img1_rectified)
    cv2.imshow("right", img2_rectified)
    # cv2.imshow("left", img1_rectified)
    # cv2.imshow("right", img2_rectified)
    cv2.imshow("depth", disp)
    center3DPoint=threeD[point1[0]:point2[0],point1[1]:point2[1],:]

    #print(center3DPoint)
    #print(selectedDepth.shape)
    #filteredDepth=[]
    #f
    # selectedDepth = np.around(threeD[point1(0):point2(0), point1(1):point2(1), 2])
    # for row in range(selectedDepth.shape[0]):
    #     for col in range(selectedDepth.shape[1]):
    #         if selectedDepth[row][col] not in excludedItems:
    #             filteredDepth.append(selectedDepth[row][col])
    #
    #
    # print(mode(filteredDepth, axis=None)[0])

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("s"):
        cv2.imwrite("./snapshot/BM_left.jpg", imgL)
        cv2.imwrite("./snapshot/BM_right.jpg", imgR)
        cv2.imwrite("./snapshot/BM_depth.jpg", disp)

camera.release()
cv2.destroyAllWindows()