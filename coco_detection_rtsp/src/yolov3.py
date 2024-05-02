"""yolov3"""
import traceback
from acllite_model import AclLiteModel

import os
import cv2
import json
import numpy as np
from threading import Thread

from util.message import *
from util.v3_anchors import anchor_v3
from util.tools import date_1, date_4, save_pillow
from util.classification import fire_post, person_post, work_clothe_post, waste_post, smoke_post, parkingspace_post

LABEL = 1
SCORE = 2
TOP_LEFT_X = 3
TOP_LEFT_Y = 4
BOTTOM_RIGHT_X = 5
BOTTOM_RIGHT_Y = 6

labels = ['car_light', 'work_clothes', 'helmet', 'intrusion', 'fire', 'smoke', 'extinguisher', 'parkingspace', 'parkingspace', 'waste']

# TODO:20230907@cmx:Load directory
fire_folder = './fire_img/'
workclothes_folder = './workclothes_img/'
# TODO: 20230911@cmx: !!! remenber 
js_file = read_json(instruction_file)

fire_type = None
try:
    if js_file["alarm"]['fire']['type'] == 1:
        fire_type = 1
    elif js_file["alarm"]['fire']['type'] == 2:
        fire_type = 2
except:
    fire_type = 2

class Yolov3(object):
    """yolov3"""

    def __init__(self, acl_resource, model_path, model_width, model_height):
        self._acl_resource = acl_resource
        self._model_width = model_width
        self._model_height = model_height
        # 20231126: encapsulated yolov3 according to model path
        self._model = AclLiteModel(model_path)

    def __del__(self):
        if self._model:
            del self._model

    def construct_image_info(self):
        """construct"""
        image_info = np.array([self._model_width, self._model_height,
                               self._model_width, self._model_height],
                              dtype=np.float32)
        return image_info

    def execute(self, data):
        """execute"""
        image_info = self.construct_image_info()
        return self._model.execute([data.resized_image, image_info])

    def post_process(self, infer_output, data):
        """post process"""
        # 2023919@cmx：labels_list
        labels_list = []

        # TODO：202301123@cmx:make file accoding to date
        current_time_str_file = date_1()
        pos_img = os.path.join(aiimg, current_time_str_file)

        # TODO:20230907@cmx:create pos_img folder
        if not os.path.exists(pos_img):
            os.makedirs(pos_img)

        print("=====log30=====")

        """post"""
        print("In yolo, infer output shape is : ", infer_output[1].shape)
        box_num = int(infer_output[1][0, 0])
        print("In yolo, box num = ", box_num)
        box_info = infer_output[0].flatten()
        scalex = data.frame_width / self._model_width
        scaley = data.frame_height / self._model_height
        if scalex > scaley:
            scaley = scalex

        # TODO:20230906@cmx: bgr_image
        image_post = data.bgr_image

        for n in range(int(box_num)):
            print("=====log31=====")
            ids = int(box_info[5 * int(box_num) + n])
            label = labels[ids]

            score = box_info[4 * int(box_num) + n]
            lt_x = int(box_info[0 * int(box_num) + n] * scaley)
            lt_y = int(box_info[1 * int(box_num) + n] * scaley)
            rb_x = int(box_info[2 * int(box_num) + n] * scaley)
            rb_y = int(box_info[3 * int(box_num) + n] * scaley)
            print("channel %s inference result: box top left(%d, %d), "
                    "bottom right(%d %d), score %s" % (data.ipcaddr, lt_x, lt_y, rb_x, rb_y, score))
            print("label:", label)  

            # TODO:20230811@cmx: 100% :start
            score = score * 100

            # TODO:20230913@cmx: if detect 
            current_time_str = date_4()
            
            # 20240206@xjk
            if (label == 'fire' or label == 'smoke') and score > js_file["alarm"][label]["reliability"]:
                labels_list.append(label)
                if fire_type == 2 and 'fire' in labels_list and 'smoke' in labels_list:
                        
                        # TODO:20240110@cmx:create fire folder
                        if not os.path.exists(fire_folder):
                            os.makedirs(fire_folder)
                        
                        save_path = os.path.join(fire_folder, '%s_%s_%s.jpg' % (label, data.channel, current_time_str))  
                        save_pillow(image_post, save_path)

                        # 带框的图片
                        image_post_2 = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                        save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % (label, data.channel, current_time_str))
                        save_pillow(image_post_2, save_path_2)

                        # 20240112:cmx: multi process
                        t = Thread(target=fire_post, args=(data.channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score))
                        t.start()
                        logger.text_log("fire:%s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score))

                        labels_list.clear()
                print("======log32======")


            # TODO:20231015@cmx: post mess
            # 20240226@xjk: switch of fire detection type
            if label == 'fire' and 'fire' in js_file["camera"]["Camera"][data.channel]['AI'].split(","):
                if fire_type == 1 and score > js_file["alarm"]['fire']['reliability']:
                        
                        # TODO:20240110@cmx:create fire folder
                        if not os.path.exists(fire_folder):
                            os.makedirs(fire_folder)
                            
                        save_path = os.path.join(fire_folder, '%s_%s_%s.jpg' % (label, data.channel, current_time_str)) 
                        save_pillow(image_post, save_path)

                        # 带框的图片
                        image_post_2 = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                        save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % (label, data.channel, current_time_str))
                        save_pillow(image_post_2, save_path_2)
                        
                        # 20240112:cmx: post fire
                        t = Thread(target=fire_post, args=(data.channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score))
                        t.start()

                        # 20240113@cmx: log of fire
                        logger.text_log("fire:%s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score))
                        
                        print("======log32======")
            elif (label == 'intrusion') and (score > js_file["alarm"]['intrusion']['reliability']) and ('intrusion' in js_file["camera"]["Camera"][data.channel]['AI'].split(",")):
                cen_x = (rb_x - lt_x) // 2 + lt_x
                cen_y = (rb_y - lt_y) // 2 + lt_y
                print("======cen_x:======", cen_x)
                print("=====cem_y:=====", cen_y)

                area_1 = js_file['alarm']['intrusion']['camera'][2]['Region']

                area_2 = json.loads(area_1)

                intru_ltx =  area_2[0]["Lx"]
                intru_lty =  area_2[0]["Ly"]
                intru_rtx =  area_2[0]["Rx"]
                intru_rty =  area_2[0]["Ry"]

                if (intru_ltx < cen_x < intru_rtx) and (intru_lty < cen_y < intru_rty):

                    # 20232221@cmx:label to intruction
                    image_post_2 = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                    save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % ('intrusion', data.channel, current_time_str))
                    save_pillow(image_post_2, save_path_2)

                    # 20240112:cmx: post intrusion
                    t = Thread(target=person_post, args=(data.channel, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))
                    t.start()
                    logger.text_log("intrusion:%s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))

                    print("======log33======")

                # TODO:20231015@cmx: post mess
            elif (label == 'work_clothes') and (score > 90) and ('workclothes' in js_file["camera"]["Camera"][data.channel]['AI'].split(",")):
                # TODO:20240110@cmx:create workclothes folder
                if not os.path.exists(workclothes_folder):
                    os.makedirs(workclothes_folder)

                img = image_post[lt_x:rb_x, lt_y:rb_y]
                print("=====log34====")
                # 20240125@xjk
                image_data_mean, _ = cv2.meanStdDev(img)
                sum_mean = image_data_mean.sum()

                # 20240315@xjk
                B_low, B_up = 0.37, 0.56
                G_low, G_up = 0.24, 0.34
                R_low, R_up = 0.19, 0.35
                
                # 20240125@xjk
                if (B_low < image_data_mean[0][0]/sum_mean < B_up) and (G_low < image_data_mean[1][0]/sum_mean < G_up) and (R_low < image_data_mean[2][0]/sum_mean < R_up):
                    save_path = os.path.join(workclothes_folder, '%s_%s_%s.jpg' % (label, data.channel, current_time_str))
                    save_pillow(image_post, save_path)

                    image_post_2 = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                    save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % (label, data.channel, current_time_str))
                    save_pillow(image_post_2, save_path_2)

                    # post workclothes
                    t = Thread(target=work_clothe_post, args=(data.channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score))
                    t.start()
                    logger.text_log("work_clothes:%s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score))
                    print("======log35======")

            # TODO:20231015@cmx: post mess
            elif (label == 'smoke') and (score > js_file["alarm"]["smoke"]["reliability"]) and ('smoke' in js_file["camera"]["Camera"][data.channel]['AI'].split(",")):
                save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % (label, data.channel, current_time_str)) 
                image_post_2 = anchor_v3(image_post, lt_x, lt_y, rb_x, rb_y)
                save_pillow(image_post_2, save_path_2)

                # 20240112:cmx: multi process
                t = Thread(target=smoke_post, args=(data.channel, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))
                t.start()
                logger.text_log("smoke:%s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))

                print("======log37======")
            # 20240306@xjk: waste
            elif (label == 'waste') and (score > js_file["alarm"]["waste"]["reliability"]) and ('waste' in js_file["camera"]["Camera"][data.channel]['AI'].split(",")): 

                image_post_2 = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % ('waste', data.channel, current_time_str))
                save_pillow(image_post_2, save_path_2)

                t = Thread(target=waste_post, args=(data.channel, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))
                t.start()
                # 20240306@xjk: log of waste
                logger.text_log("waste: %s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))
                print("======log38======")

            # 20240325@xjk: parkingspace
            elif (label == 'parkingspace') and (score > js_file["alarm"]["parkingspace"]["reliability"]) and ('parkingspace' in js_file["camera"]["Camera"][data.channel]['AI'].split(",")): 
                image_post_2 = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                save_path_2 = os.path.join(pos_img, '%s_%s_%s.jpg' % ('parkingspace', data.channel, current_time_str))
                save_pillow(image_post_2, save_path_2)

                # 20240112:cmx: multi process
                t = Thread(target=parkingspace_post, args=(data.channel, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))
                t.start()

                logger.text_log("parkingspace:%s_%s_%s_%s_%s_%s_%s_%s" % (data.ipcaddr, current_time_str, save_path_2, lt_x, lt_y, rb_x, rb_y, score))
                print("======log39======")

            elif (label == 'helmet') and (score > js_file["alarm"]["helmet"]["reliability"]) and ('helmet' in js_file["camera"]["Camera"][data.channel]['AI'].split(",")): 
                image_post = anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y)
                print("======log40======")