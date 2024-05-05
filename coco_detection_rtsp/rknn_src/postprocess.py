import time
import queue
import traceback
import threading
lock = threading.Lock()
from util.message import *

js_file = read_json(instruction_file)

class DetectData(object):
    """detecdata"""
    def __init__(self, frame_data, detect_results):
        self.frame_data = frame_data
        self.detect_results = detect_results

class Postprocess(object): 
    """post"""
    def __init__(self, detect_model):
        self._detector = detect_model
        self._channel = None         
        self._data_queue =  queue.Queue(15)
        self._start()
        self._exit = False

    def _start(self):
        thread = threading.Thread(target=self._thread_entry)            
        thread.start()

    def _thread_entry(self):   
        ret = True
        while ret: 
            if not self._data_queue.empty():
                with lock:
                    data = self._data_queue.get()
                    logger.text_log('%s正在进行功能性检验后处理' % data.frame_data.ipcaddr)
                    if isinstance(data, DetectData):
                        try:
                            self._process_detect_data(data.detect_results, 
                                                             data.frame_data)
                        except:
                            ERROR = traceback.format_exc()
                            logger.error_log(ERROR)
                        logger.text_log('%s，功能性检验后处理结束' % data.frame_data.ipcaddr)
                    elif isinstance(data, str):
                        logger.text_log("Post process thread exit")
                        self._exit = True
                        ret = False
                    else: 
                        logger.error_log("post process thread receive unkonow data")   

            
    def _process_detect_data(self, detect_results, frame_data):
        self._detector.post_process(detect_results, frame_data.input_img)  
        # ret = True                                                 
        # return ret        

    def process(self, data, detect_results):
        """process"""
        detect_data = DetectData(data, detect_results)
        # postprocessing result in queue 2
        self._data_queue.put(detect_data)

    def exit(self):
        """exit"""
        self._data_queue.put("exit")
        while self._exit == False:
            time.sleep(0.001)
