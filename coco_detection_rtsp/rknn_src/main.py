"""main"""
from rknnlite.api import RKNNLite

import os
import sys
cur_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_file_dir + "/../../../../common")

from util.message import *
from util.tools import img_preprocess

from yolov5 import Yolov5
from preprocess import Preprocess
from postprocess import DetectData, Postprocess

RKNN_MODEL = '../model/yolov5s.rknn'
DATASET = './datasets.txt'
MODEL_WIDTH = 640
MODEL_HEIGHT = 640

js_file = read_json(instruction_file)

def create_threads(detector, n, a, video_id):
    """create threads"""
    video_decoders = []

    # 20230911@cmx: multi video in time
    try:
        for i in range(n):
                preprocesser = Preprocess(js_file["camera"]['Camera'][i+a]['PlayUrl'], 
                                        len(video_id),
                                        MODEL_WIDTH, MODEL_HEIGHT)
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
    
    postprocessor = None
    # postprocessor = Postprocess(detector)

    return video_decoders, postprocessor

def main():
    """
    Function description:
        Main function
    """
    rknn_lite = RKNNLite(verbose=True, verbose_file='./inference.log')

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

    detector = Yolov5(rknn_lite, MODEL_WIDTH, MODEL_HEIGHT)

    video_decoders, postprocessor = create_threads(detector, 1, 0, [1]*0)
    if video_decoders is None:
        logger.error_log("Please check if the configuration is valid")
        return
    
    while True:
        all_process_fin = True
        for decoder in video_decoders:
            ret, data = decoder.get_data()
            data.input_img = img_preprocess(data.frame)
            
            if ret == False:                
                continue
            if data:
                detect_results = detector.execute(data)
                # postprocessor.process(data, detect_results)
                
            all_process_fin = False
        if all_process_fin:
            logger.text_log("all video decoder finish")
            break

    postprocessor.exit()

    logger.text_log("sample execute end")  

if __name__ == '__main__':
    main()
