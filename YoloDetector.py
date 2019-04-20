from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time

from KalmanFilter import ObjectPredictor

BBOX = []

path = './darknet/'


class BOX(Structure):
    _fields_ = [('x', c_float),
                ('y', c_float),
                ('w', c_float),
                ('h', c_float)]


class DETECTION(Structure):
    _fields_ = [('bbox', BOX),
                ('classes', c_int),
                ('prob', POINTER(c_float)),
                ('mask', POINTER(c_float)),
                ('objectness', c_float),
                ('sort_class', c_int)]


class IMAGE(Structure):
    _fields_ = [('w', c_int),
                ('h', c_int),
                ('c', c_int),
                ('data', POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [('classes', c_int),
                ('names', POINTER(c_char_p))]


hasGPU = True

lib = CDLL(path + 'libdarknet.so', RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

if hasGPU:
    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = \
    [c_void_p, c_int, c_int, c_float, c_float, POINTER(
        c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

if path == './darknet_mac/':
    xratio = 640.0/416.0
    yratio = 360.0/416.0
else:
    xratio = 740.0/416.0
    yratio = 416.0/416.0


def array_to_image(arr):
    import numpy as np
    arr = arr.transpose(2, 0, 1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
    data = arr.ctypes.data_as(POINTER(c_float))
    im = IMAGE(w, h, c, data)
    return im, arr


def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45, debug=False):
    im, _ = array_to_image(image)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h,
                             thresh, hier_thresh, None, 0, pnum, 0)
    num = pnum[0]
    if nms:
        do_nms_sort(dets, num, meta.classes, nms)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                if altNames is None:
                    nameTag = meta.names[i]
                else:
                    nameTag = altNames[i]
                res.append((nameTag, dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_detections(dets, num)
    return res


def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxesWithNames(detections, img, cap, text=True, color=(0, 255, 0)):
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))

        pt1 = (int(xmin * xratio), int(ymin * yratio))
        pt2 = (int(xmax * xratio), int(ymax * yratio))
        cv2.rectangle(img, pt1, pt2, color, 1)
        if text:
            cv2.putText(img,
                        detection[0],
                        (pt1[0], pt1[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        [0, 255, 0], 4)
    return img


netMain = None
metaMain = None
altNames = None


def YoloInit():
    global metaMain, netMain, altNames
    configPath = path + 'cfg/yolov3-tiny_obj.cfg'
    weightPath = path + 'yolov3-tiny_obj_last.weights'
    metaPath = path + 'data/obj.data'
    if not os.path.exists(configPath):
        raise ValueError('Invalid config path `' +
                         os.path.abspath(configPath)+'`')
    if not os.path.exists(weightPath):
        raise ValueError('Invalid weight path `' +
                         os.path.abspath(weightPath)+'`')
    if not os.path.exists(metaPath):
        raise ValueError('Invalid data file path `' +
                         os.path.abspath(metaPath)+'`')
    if netMain is None:
        netMain = load_net_custom(configPath.encode(
            'ascii'), weightPath.encode('ascii'), 0, 1)
    if metaMain is None:
        metaMain = load_meta(metaPath.encode('ascii'))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search('names *= *(.*)$', metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split('\n')
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass


def StartYoloDetection(cap, tracker, cvth, serial, debug=False, thresh=0.10):
    lastID = 0
    count = 0
    while True:
        prev_time = time.time()
        _, frame_read = cap.read()
        yaw = serial.yaw
        pitch = serial.pitch

        frame_resized = cv2.resize(frame_read,
                                   (lib.network_width(netMain),
                                    lib.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)
        detections = detect(netMain, metaMain, frame_resized, thresh=thresh)
        # time.sleep(0.15)
        tracker.update(detections)
        detections = []
        rank = []

        for item in tracker.validObjects.items():
            objID, ((cx, cy), bbox, label, _) = item
            if label == 'Blue':
                label = 'Red'
            else:
                label = 'Blue'
            label = str(objID) + '-' + label
            xmin, ymin, xmax, ymax = bbox
            w_half = int((xmax-xmin)/2) * xratio
            h_half = int((ymax-ymin)/2) * yratio
            bbox_cvh = (xmin * xratio, ymin * yratio, (xmax-xmin)
                        * xratio, (ymax-ymin) * yratio)
            bbox = (xmin, ymin, xmax-xmin, ymax-ymin)
            detections.append((label, 1., bbox))
            rank.append((objID, (cx-w_half, cy-h_half), bbox_cvh))

        count = 0
        rank.sort()
        if len(rank) > 0:
            randID = rank[0][0]
            bbox = rank[0][2]
            pix_x = rank[0][1][0]
            pix_y = rank[0][1][1]
            if randID != lastID:
                count = 0
                lastID = randID

                # Clean filter and cvth
                serial.filter = ObjectPredictor()
                serial.validate = False
                # cvth.clear()

            else:
                # print('YOLO UPDATE CVTRACKER count: ', count, ' validate: ', serial.validate)

                serial.validate = True

                # cvth.restart()
                # cvth.updateByNN(frame_read, bbox)

                # Old calibration
                # x = math.atan((pix_x - 740/2) / 693.3) * 1800 / math.pi
                # y = math.atan((pix_y - 416/2) / 693.3) * 1800 / math.pi

                # New calibration
                x = math.atan((pix_x - 740/2) / 475.3) * 1800 / math.pi
                print('calx:',pix_x)
                y = math.atan((pix_y - 416/2) / 475.3) * 1800 / math.pi
                print('caly:',pix_y)

                # serial.filter.updateSensorAbsolute(x, 0, yaw, 0)

                serial.x = int(x)
                serial.y = int(y)
        else:
            count = 0

            # Clean filter and cvth
            serial.filter = ObjectPredictor()
            serial.validate = False
            # cvth.clear()

        if debug:
            frame_read = cvDrawBoxesWithNames(
                detections, frame_read, cap, text=True)
            cv2.imshow('video', frame_read)
            #print('FPS: %.2f' % (1.0/(time.time()-prev_time)))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
