import math
import threading
import time

from can import Message

from KalmanFilter import ObjectPredictor

import numpy as np


class SerialThread(threading.Thread):
    def __init__(self, port, recvTh, connect=True, fps=1000, debug=True):
        super(SerialThread, self).__init__()
        self.fps = fps
        self.connect = connect
        self.filter = ObjectPredictor()
        self.debug = debug
        self.recvTh = recvTh

        if self.connect:
            self.dev = port

        self.x = 0
        self.y = 0
        self.send_x = 0
        self.send_y = 0
        self.validate = False
        self.sendData = []

        self.yaw = 0
        self.pitch = 0

    def numToHex(self, num):
        if(num < 0):
            num = 0
        num = bin(num)
        num = num[2: len(num)]
        data = []
        for i in range(16-len(num)):
            num = '0' + num
        data.append(int(num[0:8], 2))
        data.append(int(num[8:16], 2))
        return data

    def sendMessage(self):
        x_num = self.x + 900
        y_num = self.y + 300

        if(x_num >= 1800 or x_num <= 0 or not self.validate):
            x_num = 900
        if(y_num >= 500 or y_num <= 0 or not self.validate):
            y_num = 300

        self.send_x = int(x_num)
        self.send_y = int(y_num)
        x = self.numToHex(int(x_num))
        y = self.numToHex(int(y_num))
        self.sendData = [x[0], x[1], y[0], y[1], 0x00, 0x00, 0x00, 0x00]

        if len(self.sendData) == 8:
            self.dev.send(Message(arbitration_id=0x300, dlc=8,
                                  data=self.sendData, extended_id=False))

    def run(self):
        count_plot = 0
        while(True):

            start_time = time.time()

            # _, _ = self.filter.getPredictionAbsolute(13)

            if self.connect:
                self.sendMessage()
                if self.recvTh != None:
                    self.yaw = self.recvTh.yaw
                    self.pitch = self.recvTh.pitch

            if count_plot >= 100:
                count_plot = 0
                if self.debug:
                    print('Send: %d %d Raw: %d %d Recieve: %d %d' % (
                        self.send_
                        x, self.send_y, self.x, self.y, self.yaw, self.pitch))

            count_plot += 1

            currentTime = time.time()
            runTime = currentTime - start_time
            waitTime = 1./self.fps - runTime
            if self.debug and False:
                #print('- Filter FPS: %.2f' % (1.0/runTime))
            if(waitTime > 0):
                time.sleep(waitTime)


class RecieveThread(threading.Thread):
    def __init__(self, port):
        super(RecieveThread, self).__init__()
        self.dev = port
        self.yaw = 0
        self.pitch = 0

    def hexToNumArray(self, data):
        nums = []
        for i in range(4):
            a = data[2*i: 2*i+2]
            num1 = bin(a[0])[2:10]
            num2 = bin(a[1])[2:10]
            for i in range(8-len(num1)):
                num1 = '0' + num1
            for i in range(8-len(num2)):
                num2 = '0' + num2
            nums.append(int(num1 + num2, 2))
        return nums

    def recvMessage(self):
        frame = self.dev.recv()
        if frame.arbitration_id == 0x210:
            self.yaw = self.hexToNumArray(frame.data)[0]
            if(self.yaw < 1500):
                self.yaw = self.yaw + 8192
            self.yaw = (7200 - self.yaw) * 3600 / 8192
        if frame.arbitration_id == 0x211:
            self.pitch = self.hexToNumArray(frame.data)[0]
            self.pitch = self.pitch - 2550
            self.pitch = self.pitch * 3600 / 8192

    def run(self):
        while(True):
            self.recvMessage()


if __name__ == '__main__':
    from can.interfaces import slcan
    port = slcan.slcanBus("/dev/ttyACM0", bitrate=1000000)
    port.open()
    recvth = RecieveThread(port)
    serial = SerialThread(connect=True, port=port, debug=True, recvTh=recvth)
    recvth.start()
    serial.start()
