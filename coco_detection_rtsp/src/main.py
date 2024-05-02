"""main"""
import acl
from acllite_utils import *
from acllite_resource import AclLiteResource
from acllite_logger import log_error, log_info
from acllite_model import AclLiteModel

import os
import sys
cur_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_file_dir + "/../../../../common")

import datetime
import traceback
import multiprocessing
from constants import *
from util.message import *  # 20240314@xjk: path, logging , post_mess
from yolov3 import Yolov3
from util.tools import YUV2BGR, date_2
from preprocess import Preprocess
from postprocess import Postprocess
from Car_recognition import car_ocr

MODEL_PATH = "../model/20240331_v5.om"
MODEL_WIDTH = 640
MODEL_HEIGHT = 640
COCO_DETEC_CONF="../scripts/coco_detection.conf"

# 20230911@cmx: search how many videos
js_file = read_json(instruction_file)

def create_threads(detector, n, a, video_id, device_id):
    """create threads"""
    # config = configparser.ConfigParser()
    # config.read(COCO_DETEC_CONF)

    video_decoders = []

    # 20230911@cmx: multi video in time
    try:
        for i in range(n):
                preprocesser = Preprocess(js_file["camera"]['Camera'][i+a]['PlayUrl'], 
                                        len(video_id),
                                        MODEL_WIDTH, MODEL_HEIGHT, device_id)
                video_decoders.append(preprocesser)

                # 20240127@cmx: video_id 
                video_id.append(1)

        rtsp_num = len(video_decoders)
    except:
        Error = traceback.format_exc()
        print(Error)
        logger.error_log(Error)
    if rtsp_num == 0:
        log_error("No video stream name or addr configuration in ",
                  COCO_DETEC_CONF)
        return None, None

    postprocessor = Postprocess(detector, device_id)

    return video_decoders, postprocessor

def main():
    # 20231129@cmx: time of start
    start_time = datetime.datetime.now() 
    print("=====start_time:======", start_time)

    # 20230911@cmx: how many camera
    n = len(js_file["camera"]['Camera'])

    # 20240302@xjk: "Create processes based on the number of devices"
    count, _ = acl.rt.get_device_count()
    #count = 1

    process_list = []
    # 20240315@xjk: have been processed camera
    index_of_camera = 0
    # 20240315@xjk: index of npu
    index_of_npu = 0

    max_reder = 0

    if count == 1:
        # 20240315@xjk: max camera num one npu
        max_camera_num = 8  
        # 20240315@xjk: max process num one npu
        max_process_num = 4
        # 20240315@xjk: max camera num one process
        if max_camera_num % max_process_num == 0:

            max_reder = max_camera_num // max_process_num 
        else:

            max_reder = max_camera_num // max_process_num + 1
            # 20240315@xjk: max camera num one process

        while index_of_camera + max_reder <= max_camera_num and index_of_camera + max_reder <= n: # 20240315@xjk: 还能启动摄像头或者并且还有摄像头
            process = multiprocessing.Process(target=detect, args=(max_reder, index_of_camera, [1]*index_of_camera, index_of_npu))
            print('max_reder:', max_reder)
            print('index_of_camera:', index_of_camera)
            print('index_of_npu:', index_of_npu)
            process_list.append(process)
            index_of_camera += max_reder
        
        if index_of_camera < max_camera_num and index_of_camera < n: # 20240315@xjk: 还能启动摄像头或者并且还有摄像头
            Min = min(max_camera_num, n)
            process = multiprocessing.Process(target=detect, args=(Min - index_of_camera, index_of_camera, [1]*index_of_camera, index_of_npu))
            print('max_reder:', Min - index_of_camera)
            print('index_of_camera:', index_of_camera)
            print('index_of_npu:', index_of_npu)
            process_list.append(process)
            index_of_camera = Min

    else:
        max_camera_num = 12

        # 20240315@xjk: max process num one npu
        max_process_num = 16

        if max_camera_num % max_process_num == 0:

            max_reder = max_camera_num // max_process_num 
        else:

            max_reder = max_camera_num // max_process_num + 1
            # 20240315@xjk: max camera num one process

        while index_of_camera + max_reder <= max_camera_num * count and index_of_camera + max_reder <= n: # 20240315@xjk: 还能启动摄像头或者并且还有摄像头
            if index_of_camera + max_reder < max_camera_num * (index_of_npu + 1):
                process = multiprocessing.Process(target=detect, args=(max_reder, index_of_camera, [1]*index_of_camera, index_of_npu))
                print('max_reder:', max_reder)
                print('index_of_camera:', index_of_camera)
                print('index_of_npu:', index_of_npu)
                process_list.append(process)
                index_of_camera += max_reder
            elif index_of_camera <= max_camera_num* (index_of_npu + 1):
                process = multiprocessing.Process(target=detect, args=(max_camera_num* (index_of_npu + 1) - index_of_camera, index_of_camera, [1]*index_of_camera, index_of_npu))
                print('max_reder:', max_camera_num* (index_of_npu + 1) - index_of_camera)
                print('index_of_camera:', index_of_camera)
                print('index_of_npu:', index_of_npu)
                process_list.append(process)
                index_of_camera = max_camera_num* (index_of_npu + 1)
                index_of_npu += 1
        
        while index_of_camera < max_camera_num * count and index_of_camera < n: # 20240315@xjk: 还能启动摄像头或者并且还有摄像头
            Min = min(max_camera_num * count, n)
            if Min < max_camera_num* (index_of_npu + 1): # index_of_camera + (Min - index_of_camera)
                process = multiprocessing.Process(target=detect, args=(Min - index_of_camera, index_of_camera, [1]*index_of_camera, index_of_npu))
                print('max_reder:', Min - index_of_camera)
                print('index_of_camera:', index_of_camera)
                print('index_of_npu:', index_of_npu)
                process_list.append(process)
                index_of_camera = Min
            else:
                process = multiprocessing.Process(target=detect, args=(max_camera_num* (index_of_npu + 1) - index_of_camera, index_of_camera, [1]*index_of_camera, index_of_npu))
                print('max_reder:', max_camera_num* (index_of_npu + 1) - index_of_camera)
                print('index_of_camera:', index_of_camera)
                print('index_of_npu:', index_of_npu)
                process_list.append(process)
                index_of_camera = max_camera_num* (index_of_npu + 1)
                index_of_npu += 1

    for process in process_list:
        process.start()
    
    for process in process_list:
        process.join()


def detect(n, a, video_id, device_id):
    """
    Function description:
        Main function
    """
    acl_resource = AclLiteResource(device_id)
    acl_resource.init()   
    
    detector = Yolov3(acl_resource, MODEL_PATH, MODEL_WIDTH, MODEL_HEIGHT)

    # 20231215@cmx: load weights
    MODEL_PATH_2 = './weights/detect_nonaipp.om'
    detect_model = AclLiteModel(MODEL_PATH_2)
    
    MODEL_PATH_3 = './weights/plate_rec_color-2.om'
    plate_rec_model = AclLiteModel(MODEL_PATH_3)

    video_decoders, postprocessor = create_threads(detector, n, a, video_id, device_id)
    if video_decoders is None:
        log_error("Please check the configuration in %s is valid"
                %(COCO_DETEC_CONF))
        return
    
    # 20240203@cmx: judge the host if ok
    host_feedback = {"host_status":"hi, status of host is OK"}
    post_mess(host_feedback)

    while True: 
        all_process_fin = True
        # 20240314@xjk: index of camera
        for decoder in video_decoders:
            # 20240314@xjk: time marker
            current_time_str_1 = current_time_str_2 = current_time_str_3 = current_time_str_4 = 0
            try:
                ret, data = decoder.get_data()
                if ret and data:
                    
                    current_time_str_1 = date_2()

                    if data.bgr_image is None:
                        data.bgr_image = YUV2BGR(data.frame)

                    detect_results = detector.execute(data)
                    
                    postprocessor.process(data, detect_results)

                    current_time_str_2 = date_2()  

                # 20240325@xjk: car plate recognition
                ret, plate_data = decoder.get_car_data()
                if ret and plate_data and (('plate' == js_file["camera"]["Camera"][plate_data.channel]['AI'].split(",")) or ('plate' in js_file["camera"]["Camera"][plate_data.channel]['AI'])):

                    current_time_str_3 = date_2()

                    if plate_data.bgr_image is None:
                        plate_data.bgr_image = YUV2BGR(plate_data.frame)
                        
                    car_ocr(plate_data.channel, plate_data, detect_model, plate_rec_model)
                    current_time_str_4 = date_2()

                # 20240314@xjk: time marker
                if current_time_str_2 - current_time_str_1 != 0:
                    logger.text_log("第%d个npu，功能性检验总耗时:%s" %(device_id, str(current_time_str_2 - current_time_str_1)))
                if current_time_str_4 - current_time_str_3 != 0:
                    logger.text_log("第%d个npu，车辆车牌检验总耗时:%s" %(device_id, str(current_time_str_4 - current_time_str_3)))
                    if current_time_str_2 - current_time_str_1 != 0:
                        logger.text_log("第%d个npu，所有检测共总耗时:%s" %(device_id, str(current_time_str_4 - current_time_str_1)))
            except:
                Error = traceback.format_exc()
                print(Error)
                logger.error_log(Error)

            # prevent the process from exiting
            all_process_fin = False

        if all_process_fin:
            log_info("all video decoder finish")
            break
    postprocessor.exit()
    log_info("sample execute end") 
    

if __name__ == '__main__':
    main()
