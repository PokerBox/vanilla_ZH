import cv2
import time
import threading
import imutils
import numpy as np


class VideoProcessor(threading.Thread):
    #def __init__(self, source=1, fps=None, debug=False, resolution=None, stereo=True):
    # left_camera_matrix = np.array([[832.435658123356, 0., 679.097692053230],
    #                                [0., 834.154701860582, 520.052455316846],
    #                                [0., 0., 1]])
    # left_distortion = np.array(
    #     [-0.377556841877811, 0.119187796731564, 0.000244059708238597, 0.000942934866738105])

    # right_camera_matrix = np.array([[831.698786244524, 0., 673.352686245399],
    #                                 [0, 836.533841311744, 519.093704144343],
    #                                 [0., 0., 1]])
    # right_distortion = np.array(
    #     [-0.346760277995920, 0.0848078234665875, 0.00159692034796570, -0, 0.0000622650672924687])
    # R = np.array([[0.999642944780343, 0.00110588320819119, -0.0266975649304055],
    #               [-0.00120272633595674, 0.999992754766322, -0.00361162902620857],
    #               [0.0266933774604147, 0.00364244933966102, 0.999637032208473]])
    # R = np.transpose(R)
    # T = np.array([-5.93877302419152, -0.0259699410014745, 0.245447082761350])
    # img_size = (1280, 960)

    # R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(left_camera_matrix, left_distortion,
    #                                                                   right_camera_matrix, right_distortion, img_size,
    #                                                                   R,
    #                                                                   T, alpha=0.5)
    # left_map1, left_map2 = cv2.initUndistortRectifyMap(left_camera_matrix, left_distortion, R1, P1, img_size,
    #                                                    cv2.CV_16SC2)
    # right_map1, right_map2 = cv2.initUndistortRectifyMap(right_camera_matrix, right_distortion, R2, P2, img_size,
    #                                                      cv2.CV_16SC2)

    def __init__(self, source=1, fps=None, debug=False, resolution=(1280, 720), stereo=False):
        super(VideoProcessor, self).__init__()
        try:
            self.__stream = cv2.VideoCapture(source, cv2.CAP_V4L)
        except:
            self.__stream = cv2.VideoCapture(source)

        # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # self.__stream.set(cv2.CAP_PROP_FOURCC, fourcc)
        self.__stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.__stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.__stream.set(cv2.CAP_PROP_FPS, 120)

        self.fps = fps
        self.stereo = stereo
        self.debug = debug
        self.resolution = resolution
        self.timestamp = time.time()

        _, self.__frame = self.__stream.read()
        self.__frame = imutils.rotate(self.__frame, 180)
        
        if self.stereo:
            # self.resolution = (int(self.__stream.get(
            #     cv2.CAP_PROP_FRAME_WIDTH)), int(self.__stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self.resolution = (1280, 720)

    def run(self):
        while True:
            prevTime = time.time()
            self.timestamp = prevTime
            _, frame = self.__stream.read()
            if self.debug:
                runTime = time.time() - prevTime
                print('Video Processor FPS: %.2f' % (1./runTime))
            frame = cv2.resize(frame, (740, 416), interpolation=cv2.INTER_LINEAR)
            self.__frame = imutils.rotate(frame, 180)

            # self.__frame = self.processing(frame)
            # 
            # waitTime = 1.0/self.fps - runTime
            # if waitTime < 0:
            #     if self.debug:
            #         print('Video stream FPS low: %.2f' % (1.0/runTime))
            # else:
            #     if self.debug:
            #         print('Video stream FPS: %.2f' % (self.fps))
            #     time.sleep(waitTime*0.98)

    def processing(self, frame):
        # frame = frame[:, 0:int(self.__stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)]
        if self.stereo:
            frame = self.rectify(frame)
        # frame = cv2.resize(
        #       frame, (self.resolution[0], self.resolution[1]), interpolation=cv2.INTER_LINEAR)
        # frame = cv2.resize(
        #       frame, (960,540), interpolation=cv2.INTER_LINEAR)

        return frame

    def rectify(self, frame):
        frame1 = frame[:, 0:1280]
        img1_rectified = cv2.remap(
            frame1, VideoProcessor.left_map1, VideoProcessor.left_map2, cv2.INTER_LINEAR)
        img1_rectified = img1_rectified[self.point1[1]
            :self.point2[1], self.point1[0]:self.point2[0], :]

        # frame2 = frame[:, 1280:]
        # img2_rectified = cv2.remap(frame2, VideoProcessor.right_map1, VideoProcessor.right_map2, cv2.INTER_LINEAR)
        # img2_rectified = img2_rectified[self.point1[1]:self.point2[1], self.point1[0]:self.point2[0], :]
        return img1_rectified

    def isOpened(self):
        return self.__stream.isOpened()

    def release(self):
        self.__stream.release()

    def read(self):
        return True, self.__frame

    # def stop(self):
    #    self._stop_event.set()


if __name__ == '__main__':
    import cv2
    cap = VideoProcessor(1, fps=120, stereo=False, debug=True)
    cap.start()
    while(True):
        _, frame = cap.read()
        # print(frame.shape)
        # print(frame)
        cv2.imshow('webcam', frame)
        cv2.waitKey(1)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
