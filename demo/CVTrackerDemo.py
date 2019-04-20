import time
import cv2
from random import randint

trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD',
                'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']

trackerType = "MEDIANFLOW" 

# only CSRT and MEDIANFLOW and TLD and MOSSE worked
# CSRT is only track one object
# MEDIANFLOW MOSSE are sensitive but feedback failure correctly
# TLD works best


def createTrackerByName(trackerType):
    if trackerType == trackerTypes[0]:
        tracker = cv2.TrackerBoosting_create()
    elif trackerType == trackerTypes[1]:
        tracker = cv2.TrackerMIL_create()
    elif trackerType == trackerTypes[2]:
        tracker = cv2.TrackerKCF_create()
    elif trackerType == trackerTypes[3]:
        tracker = cv2.TrackerTLD_create()
    elif trackerType == trackerTypes[4]:
        tracker = cv2.TrackerMedianFlow_create()
    elif trackerType == trackerTypes[5]:
        tracker = cv2.TrackerGOTURN_create()
    elif trackerType == trackerTypes[6]:
        tracker = cv2.TrackerMOSSE_create()
    elif trackerType == trackerTypes[7]:
        tracker = cv2.TrackerCSRT_create()
    else:
        tracker = None
        print('Incorrect tracker name')
        print('Available trackers are:')
        for t in trackerTypes:
            print(t)

    return tracker


cap = cv2.VideoCapture(0)
_, frame = cap.read()

bboxes = []
colors = []

frame = cv2.resize(
    frame, (640, 360), interpolation=cv2.INTER_LINEAR)
bbox = cv2.selectROI('Draw BBOX', frame, fromCenter=False)
bboxes.append(bbox)
colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
print("Press q to quit selecting boxes and start tracking")

print('Selected bounding boxes {}'.format(bboxes))


multiTracker = cv2.MultiTracker_create()

for bbox in bboxes:
    multiTracker.add(createTrackerByName(trackerType), frame, bbox)
    colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
# multiTracker.add(createTrackerByName(trackerType), frame, (123, 239, 65, 56))
# colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))


while cap.isOpened():
    prev_time = time.time()
    _, frame = cap.read()
    frame = cv2.resize(
        frame, (640, 360), interpolation=cv2.INTER_LINEAR)

    

    success, boxes = multiTracker.update(frame)
    print(success)
    if(success):
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors[i], 2, 1)

    cv2.imshow('MultiTracker', frame)

    print("FPS: %.2f" % (1.0/(time.time()-prev_time)))
    print(boxes)
    # cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()