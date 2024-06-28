import os
from threading import Thread
import cv2
import numpy as np
from util.message import *
from util.tools import date_1, date_4, save_pillow

OBJ_THRESH = 0.5
NMS_THRESH = 0.15
IMG_SIZE = 640
CLASSES = ('intrusion', 'fire', 'smoke')

current_time_str_file = date_1() # 获取日期 2024-05-16
pos_img = os.path.join(aiimg, current_time_str_file) # 拼接路径 /opt/xdiot/xdexchange/aiimg/2024-05-16
if not os.path.exists(pos_img):
    os.makedirs(pos_img)

def scale_coords(img1_shape, coords, img0_shape):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    # calculate from img0_shape
    gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
    pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords

def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0] = np.clip(boxes[:, 0], 0, img_shape[1])  # x1
    boxes[:, 1] = np.clip(boxes[:, 1], 0, img_shape[0])  # y1
    boxes[:, 2] = np.clip(boxes[:, 2], 0, img_shape[1])  # x2
    boxes[:, 3] = np.clip(boxes[:, 3], 0, img_shape[0])  # y2

def xywh2xyxy(x):
    # Convert [x, y, w, h] to [x1, y1, x2, y2]
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def process(input, mask, anchors):
    anchors = [anchors[i] for i in mask]
    grid_h, grid_w = map(int, input.shape[0:2])

    box_confidence = input[..., 4]
    box_confidence = np.expand_dims(box_confidence, axis=-1)

    box_class_probs = input[..., 5:]

    box_xy = input[..., :2]*2 - 0.5

    col = np.tile(np.arange(0, grid_w), grid_w).reshape(-1, grid_w)
    row = np.tile(np.arange(0, grid_h).reshape(-1, 1), grid_h)
    col = col.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
    row = row.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
    grid = np.concatenate((col, row), axis=-1)
    box_xy += grid
    box_xy *= int(IMG_SIZE/grid_h)

    box_wh = pow(input[..., 2:4]*2, 2)
    box_wh = box_wh * anchors

    box = np.concatenate((box_xy, box_wh), axis=-1)

    return box, box_confidence, box_class_probs


def filter_boxes(boxes, box_confidences, box_class_probs):
    """Filter boxes with box threshold. It's a bit different with origin yolov5 post process!
    # Arguments
        boxes: ndarray, boxes of objects.
        box_confidences: ndarray, confidences of objects.
        box_class_probs: ndarray, class_probs of objects.
    # Returns
        boxes: ndarray, filtered boxes.
        classes: ndarray, classes for boxes.
        scores: ndarray, scores for boxes.
    """
    boxes = boxes.reshape(-1, 4)
    box_confidences = box_confidences.reshape(-1)
    box_class_probs = box_class_probs.reshape(-1, box_class_probs.shape[-1])

    _box_pos = np.where(box_confidences >= OBJ_THRESH)
    boxes = boxes[_box_pos]
    box_confidences = box_confidences[_box_pos]
    box_class_probs = box_class_probs[_box_pos]

    class_max_score = np.max(box_class_probs, axis=-1)
    classes = np.argmax(box_class_probs, axis=-1)
    _class_pos = np.where(class_max_score >= OBJ_THRESH)

    boxes = boxes[_class_pos]
    classes = classes[_class_pos]
    scores = (class_max_score* box_confidences)[_class_pos]
    return boxes, classes, scores


def nms_boxes(boxes, scores):
    """Suppress non-maximal boxes.
    # Arguments
        boxes: ndarray, boxes of objects.
        scores: ndarray, scores of objects.
    # Returns
        keep: ndarray, index of effective boxes.
    """
    x = boxes[:, 0]
    y = boxes[:, 1]
    w = boxes[:, 2] - boxes[:, 0]
    h = boxes[:, 3] - boxes[:, 1]

    areas = w * h
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x[i], x[order[1:]])
        yy1 = np.maximum(y[i], y[order[1:]])
        xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
        yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])

        w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
        h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
        inter = w1 * h1

        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        inds = np.where(ovr <= NMS_THRESH)[0]
        order = order[inds + 1]
    keep = np.array(keep)
    return keep


def yolov5_post_process(input_data, frame):
    masks = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    anchors = [[10, 13], [16, 30], [33, 23], [30, 61], [62, 45],
               [59, 119], [116, 90], [156, 198], [373, 326]]

    boxes, classes, scores = [], [], []
    for input, mask in zip(input_data, masks):
        b, c, s = process(input, mask, anchors)
        b, c, s = filter_boxes(b, c, s)
        boxes.append(b)
        classes.append(c)
        scores.append(s)

    boxes = np.concatenate(boxes)
    boxes = xywh2xyxy(boxes)
    classes = np.concatenate(classes)
    scores = np.concatenate(scores)

    nboxes, nclasses, nscores = [], [], []
    for c in set(classes):
        inds = np.where(classes == c)
        b = boxes[inds]
        c = classes[inds]
        s = scores[inds]

        keep = nms_boxes(b, s)

        nboxes.append(b[keep])
        nclasses.append(c[keep])
        nscores.append(s[keep])

    if not nclasses and not nscores:
        return None, None, None

    boxes = np.concatenate(nboxes)
    classes = np.concatenate(nclasses)
    scores = np.concatenate(nscores)
    boxes = scale_coords((IMG_SIZE, IMG_SIZE), boxes, frame.shape)
    return boxes, classes, scores
           
class Yolov5(object):
    """yolov3"""

    def __init__(self, Rknn_model, IMG_SIZE):
        self._Rknn_model = Rknn_model
        self._model_width = IMG_SIZE
        self._model_height = IMG_SIZE

    def __del__(self):
        if self._Rknn_model:
            self._Rknn_model.release()

    def execute(self, data):
        """execute"""
        input = data.input_img.reshape(1, 640, 640, 3)
        return self._Rknn_model.inference(inputs=[input], data_format='nhwc')

    def post_process(self, outputs, data):
        img = data.input_img
        frame = data.frame
        input0_data = outputs[0]
        input1_data = outputs[1]
        input2_data = outputs[2]

        input0_data = input0_data.reshape([3, -1]+[80, 80])
        input1_data = input1_data.reshape([3, -1]+[40, 40])
        input2_data = input2_data.reshape([3, -1]+[20, 20])


        input_data = list()
        input_data.append(np.transpose(input0_data, (2, 3, 0, 1)))
        input_data.append(np.transpose(input1_data, (2, 3, 0, 1)))
        input_data.append(np.transpose(input2_data, (2, 3, 0, 1)))

        boxes, classes, scores = yolov5_post_process(input_data, frame)

        if boxes is not None:
            for box, score, cl in zip(boxes, scores, classes):
                label = CLASSES[cl]
                score = int(score * 100)
                #20240516@xjk 如果检测到的类别在配置文件中，且置信度大于配置文件中的置信度，则保存图片
                if label in js_file['camera'][data.channel]['ai'] and score > js_file['camera'][data.channel]['ai'][label]['reliability']:
                    left, top, right, bottom = box
                    print('class: {}, score: {}'.format(label, score))
                    print('box coordinate left,top,right,down: [{}, {}, {}, {}]'.format(left, top, right, bottom))
                    left = int(left)
                    top = int(top)
                    right = int(right)
                    bottom = int(bottom)

                    # 20240516@xjk 画框
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 1)
                    cv2.putText(frame, '{0} {1:.2f}'.format(label, score),
                                (left, bottom + 6),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 0, 255), 1)
                    
                    current_time_str = date_4()
                    save_path = os.path.join(pos_img, '%s_%s_%s.jpg'%(label, data.ipcaddr, current_time_str))
                    save_pillow(frame, save_path)

                    # 20240516@xjk 上报
                    if label == 'intrusion':
                        t = Thread(target=intrusion_post, args=(data.channel, current_time_str, save_path, left, top, right, bottom, score))
                        t.start()
                    if label == 'fire':
                        t = Thread(target=fire_post, args=(data.channel, current_time_str, save_path, left, top, right, bottom, score))
                        t.start()
                    if label == 'smoke':
                        t = Thread(target=smoke_post, args=(data.channel, current_time_str, save_path, left, top, right, bottom, score))
                        t.start()

        