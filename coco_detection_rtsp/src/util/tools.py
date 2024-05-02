import os
import cv2
import logging  
import datetime
import numpy as np
from PIL import Image
from logging.handlers import TimedRotatingFileHandler

def date_1():
    current_time_file = datetime.datetime.now()
    current_time_str_file = current_time_file.strftime("%Y-%m-%d")
    current_time_str_file = str(current_time_str_file)
    return current_time_str_file

def date_2():
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%M%S.%f")
    current_time_str_float = float(current_time_str)
    return current_time_str_float

def date_3():
    # TODO:20230906@cmx:Save images
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%H%M%S%f")[:-3]
    current_time_str = str(current_time_str)
    return current_time_str

def date_4():
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y%m%d%H%M%S.%f")[:-3]
    current_time_str = str(current_time_str)
    return current_time_str

# 20240301@xjk: save pillow
def save_pillow(img, path, new_size=(1280, 720)):
    im = Image.fromarray(img)
    im_resized = im.resize(new_size)
    im_resized.save(path)

# 20240314@xjk: YUV420SP2BGR
def YUV2BGR(img):
    data = img.byte_data_to_np_array()

    # 获取图像的宽度和高度
    width = img.width
    height = img.height

    yuv = np.frombuffer(data, dtype=np.uint8)
    yuv = yuv.reshape(height*3//2, width)

    bgr_image = cv2.cvtColor(yuv, cv2.COLOR_YUV420sp2BGR)
    return bgr_image

# 20240314@xjk:  logging class
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
        self.logger.info(text)
    
    def error_log(self, text):
        self.logger.error(text)

