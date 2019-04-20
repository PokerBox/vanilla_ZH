from canard import can
from canard.hw import cantact

dev = cantact.CantactDev("/dev/ttyACM0") # Connect to CANable that enumerated as ttyACM0
dev.set_bitrate(1000000) # Set the bitrate to a 1Mbaud
dev.start() # Go on the bus
count = 0
while True:
    count += 1
    frame = dev.recv() # Receive a CAN frame
    dev.send(frame) # Echo the CAN frame back out on the bus
    print(str(count) + ": " + str(frame)) # Print out the received frame