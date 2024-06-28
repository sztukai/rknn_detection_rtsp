"""main"""
import os
import sys
import datetime
import multiprocessing
from rknnlite.api import RKNNLite
cur_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_file_dir + "/../../../../common")

from util.message import *
from util.tools import img_preprocess, date_2

from yolov5 import Yolov5
from preprocess import Preprocess
from postprocess import Postprocess

RKNN_MODEL = '/opt/xdiot/aictrl/rknn_detection_rtsp/model/yolov5s.rknn'
DATASET = './datasets.txt'
IMG_SIZE = 640

def create_threads(detector, n, a, video_id):
    """create threads"""
    video_decoders = []

    # 20230911@cmx: multi video in time
    try:
        for i in range(n):
                preprocesser = Preprocess(js_file["camera"][i+a]['playurl'], 
                                        len(video_id),
                                        IMG_SIZE)
                video_decoders.append(preprocesser)

                # 20240127@cmx: video_id 
                video_id.append(1)

        rtsp_num = len(video_decoders)
    except:
        Error = traceback.format_exc()
        logger.error_log(Error)
    if rtsp_num == 0:
        logger.error_log("No video stream name or addr configuration")
        return None, None
    
    postprocessor = Postprocess(detector)

    return video_decoders, postprocessor

def detect(n, a, video_id):
    """
    Function description:
        Main function
    """
    rknn_lite = RKNNLite(verbose=False)

    print('--> Loading model')
    ret = rknn_lite.load_rknn(path=RKNN_MODEL)
    if ret != 0:
        print('Load model failed!')
        exit(ret)
    print('done')

    # Init runtime environment
    print('--> Init runtime environment')
    ret = rknn_lite.init_runtime()
    if ret != 0:
        print('Init runtime environment failed!')
        exit(ret)
    print('done')

    detector = Yolov5(rknn_lite, IMG_SIZE)

    video_decoders, postprocessor = create_threads(detector, n, a, video_id)
    if video_decoders is None:
        logger.error_log("Please check if the configuration is valid")
        return
    
    while True:
        all_process_fin = True
        for decoder in video_decoders:
            current_time_str_1 = current_time_str_2 = 0
            try:
                ret, data = decoder.get_data()  
                if data:
                    current_time_str_1 = date_2()
                    data.input_img = img_preprocess(data.frame) # img  img_width=640 img_height=640
                    logger.text_log('%s图片预处理完成。' % data.ipcaddr)
                    detect_results = detector.execute(data)
                    postprocessor.process(data, detect_results)
                    current_time_str_2 = date_2()
                    if current_time_str_2 - current_time_str_1 != 0:
                        logger.text_log("共耗时: %s" % (current_time_str_2 - current_time_str_1))
            except:
                ERROR = traceback.format_exc()
                logger.error_log(ERROR)
            all_process_fin = False
        if all_process_fin:
            logger.text_log("all video decoder finish")
            break

    postprocessor.exit()

    logger.text_log("sample execute end")  

def main():
    start_time = datetime.datetime.now() 
    print("=====start_time:======", start_time)
    n = len(js_file['camera'])

    process_list = [] # 进程列表
    max_process_num = 1 # 最大进程数
    max_camera_num = 5 # 最大运行摄像头数
    index_of_camera = 0 # 摄像头索引
    max_reader = 0 # 一进程处理的摄像头数
    if max_camera_num % max_process_num == 0:
        max_reader = max_camera_num // max_process_num
    else:
        max_reader = max_camera_num // max_process_num + 1
    while index_of_camera + max_reader <= max_camera_num and index_of_camera + max_reader <= n: # 20240315@xjk: 还能启动摄像头或者并且还有摄像头
            process = multiprocessing.Process(target=detect, args=(max_reader, index_of_camera, [1]*index_of_camera))
            print('max_reader:', max_reader)
            print('index_of_camera:', index_of_camera)
            process_list.append(process)
            index_of_camera += max_reader
        
    if index_of_camera < max_camera_num and index_of_camera < n: # 20240315@xjk: 还能启动摄像头或者并且还有摄像头
        Min = min(max_camera_num, n)
        process = multiprocessing.Process(target=detect, args=(Min - index_of_camera, index_of_camera, [1]*index_of_camera))
        print('max_reader:', Min - index_of_camera)
        print('index_of_camera:', index_of_camera)
        process_list.append(process)
        index_of_camera = Min

    for process in process_list:
        process.start()
    
    for process in process_list:
        process.join()

if __name__ == '__main__':
    main()
