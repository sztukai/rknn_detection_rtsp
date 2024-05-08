import os
import cv2
import logging  
import datetime
from logging.handlers import TimedRotatingFileHandler
from PIL import Image

def date_1():
    current_time_file = datetime.datetime.now()
    current_time_str_file = current_time_file.strftime("%Y-%m-%d")
    current_time_str_file = str(current_time_str_file)
    return current_time_str_file

def date_4():
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y%m%d%H%M%S.%f")[:-3]
    current_time_str = str(current_time_str)
    return current_time_str

def save_pillow(img, path, new_size=(1280, 720)):
    im = Image.fromarray(img)
    # im_resized = im.resize(new_size)
    # im_resized.save(path)
    im.save(path)

def letterbox(im, new_shape=(640, 640), color=(0, 0, 0)):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)

def img_preprocess(img, MODEL_WIDTH=640, MODEL_HEIGHT=640):
    # 1. change form
    cv2.imwrite('frame.jpg', img)
    # 2. resize
    h0, w0 = img.shape[:2]
    r = 640 / max(h0, w0)
    if r != 1:
        interp = cv2.INTER_AREA if r < 1 else cv2.INTER_LINEAR
        img = cv2.resize(img, (int(w0 * r), int(h0 * r)), interpolation=interp)
    # 3. padding
    img, ratio, (dw, dh) = letterbox(img, new_shape=(MODEL_WIDTH, MODEL_HEIGHT))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


class TextLogger: 
    def __init__(self, log_location="./log_log/", Logger_name='TextLog'):
        if not os.path.exists(log_location):
            os.makedirs(log_location)

        self.log_location = log_location
        self.current_time_str_log = date_1()
        self.log_file_name = self.log_location + "%s.log" % self.current_time_str_log

        self.logger = logging.getLogger(Logger_name)
        self.logger.setLevel(logging.INFO)

        # 创建一个每天轮转的handler
        self.handler = TimedRotatingFileHandler(self.log_file_name, when='midnight', interval=1, backupCount=7)
        self.handler.suffix = "%Y-%m-%d"
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        self.post_count = 0
        
    def text_log(self, text):
        print(text)
        self.logger.info(text)
    
    def error_log(self, text):
        print(text)
        self.logger.error(text)
