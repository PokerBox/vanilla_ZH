from can.interfaces import slcan
from can import Message
import math
dev = slcan.slcanBus("/dev/ttyACM0", bitrate=1000000)
dev.open()

def numToHex(num):
    num = bin(num)
    num = num[2: len(num)]
    data = []
    for i in range(16-len(num)):
        num = "0" + num
    data.append(int(num[0:8], 2))
    data.append(int(num[8:16], 2))
    return data


import time
for i in range(10000):
    starttime = time.time()
    x = int(100*math.sin(i/500)+900)
    y = 300
    x = numToHex(x)
    y = numToHex(y)
    data = [x[0], x[1], y[0], y[1], 0x00, 0x00, 0x00, 0x00]
    dev.send(Message(arbitration_id=0x300, dlc=8,
                                  data=data, extended_id=False))
    print("FPS: ", 1./(time.time()-starttime))
