from can.interfaces import slcan
port = slcan.slcanBus("/dev/ttyACM0", bitrate=1000000)
port.close()
