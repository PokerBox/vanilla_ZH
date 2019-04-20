import cv2, numpy as np
#Define color range
#NOTE: Opencv HSV ranges from (0,0,0) to (179,255,255)
#blue center:120    red center:180
blueLower = np.array([105,102,153]) #60% = 153 40%=102
blueUpper = np.array([135,255,255])

redLower1 = np.array([165,102,153])
redUpper1 = np.array([179,255,255])

redLower2 = np.array([0,102,153])
redUpper2 = np.array([15,255,255])
threshold=100
def process(rects, ignoredLabels=None, currentFrame=None, debugMode=False):
    """
    Pre-process detection results returned by YOLO, including:
        1. changing BBox format
        2. (Optional) double check if detected color matches the majority of color pixels (either blue or red)
    :param rects: result returned by YOLO
    :param ignoredLabels: labels (including the corresponding bbox) that will be ignored
    :param frame: (Optional) check if color matches label if frame is set to the video frame at the time of detection
    :return: processed detection result
    """
    rectsOld = rects
    rects = []
    if currentFrame is not None:
        currentFrame= cv2.cvtColor(currentFrame, cv2.COLOR_BGR2HSV)
    for item in rectsOld:
        label, _, bbox = item
        if ignoredLabels is None or label not in ignoredLabels:
            #Convert bbox from (xmin, ymin, width, height) to (xmin, ymin, xmax, ymax)
            bbox=(bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
            if currentFrame is not None:
                #Check color
                for item in rectsOld:
                    subFrame = currentFrame[bbox[0]:bbox[2],bbox[1]:bbox[3],:]
                    blueMask = cv2.inRange(subFrame, blueLower, blueUpper)
                    redMask1 = cv2.inRange(subFrame, redLower1, redUpper1)
                    redMask2 = cv2.inRange(subFrame, redLower2, redUpper2)
                    redMask=redMask1+redMask2
                    #print(blueMask.shape)
                    cv2.imshow("Blue", blueMask)
                    cv2.imshow("Red", redMask)
                    cv2.waitKey(0)
                    blueCount=np.count_nonzero(blueMask)
                    redCount=np.count_nonzero(redMask)
                    #print(blueCount,' ', redCount)
                    if (blueCount>threshold or redCount>threshold):
                        if (blueCount>redCount):
                            newLabel='Blue'
                        else:
                            newLabel='Red'
                        if debugMode:
                            print(newLabel,': ',blueCount,' ', redCount)
                            # if newLabel!=label:
                            #     print(label,' is corrected to ', newLabel)
            rects.append([bbox, label])
    return rects
