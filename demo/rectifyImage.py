"""
Rectify image based on camera type
"""
import numpy as np
import cv2
class RectifyImage:
    def __init__(self, cameraName, imgWidth, imgHeight):
        resolutionString=imgWidth+'_'+imgHeight
        self.isStereo=False
        if cameraName=='stereo1':
            self.isStereo=True
            leftCameraMatrix=np.loadtxt(cameraName+resolutionString+'_leftCameraMatrix.txt')
            rightCameraMatrix = np.loadtxt(cameraName + resolutionString + 'rightCameraMatrix.txt')
            leftDistortion = np.loadtxt(cameraName + resolutionString + 'leftDistortion.txt')
            rightDistortion= np.loadtxt(cameraName + resolutionString + 'rightDistortion.txt')
            R = np.loadtxt(cameraName + resolutionString + 'R.txt')
            T = np.loadtxt(cameraName + resolutionString + 'T.txt')
            imgSize=(imgWidth,imgHeight)
            R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(leftCameraMatrix, leftDistortion,
                                                                              rightCameraMatrix, rightDistortion,
                                                                              imgSize,
                                                                              R,
                                                                              T, alpha=0.5)
            self.left_map1, self.left_map2 = cv2.initUndistortRectifyMap(leftCameraMatrix, leftDistortion, R1, P1, imgSize,
                                                               cv2.CV_16SC2)
            self.right_map1, self.right_map2 = cv2.initUndistortRectifyMap(rightCameraMatrix, rightDistortion, R2, P2,
                                                                 imgSize,
                                                                 cv2.CV_16SC2)

            # Mystery points for cropping
            self.point1 = (30, 100)
            self.point2 = (1278, 802)
        else:
            self.cameraMatrix=np.loadtxt(cameraName+resolutionString+'cameraMatrix.txt')
            self.cameraDistortion = np.loadtxt(cameraName + resolutionString + 'cameraDistortion.txt')

    def rectify(self, frame, frameType=None):
        assert (not self.isStereo) or (self.isStereo and (frameType is 'left' or frameType is 'right')), "frameType (left or right) is required for stereo camera"
        if self.isStereo:
            if frameType=='left':
                img1_rectified = cv2.remap(
                    frame, self.left_map1, self.left_map2, cv2.INTER_LINEAR)
                result = img1_rectified[self.point1[1]
                                                :self.point2[1], self.point1[0]:self.point2[0], :]
            elif frameType=='right':
                img2_rectified = cv2.remap(frame, self.right_map1, self.right_map2, cv2.INTER_LINEAR)
                result = img2_rectified[self.point1[1]:self.point2[1], self.point1[0]:self.point2[0], :]
        else:
            result = cv2.undistort(frame, cameraMatrix=self.cameraMatrix, distCoeffs=self.cameraDistortion)
        return result