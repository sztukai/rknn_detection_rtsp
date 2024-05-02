"""postprocess"""
import traceback
import acl
import acllite_utils as utils
from acllite_logger import log_error, log_info

import time
import queue
from util.message import *
import threading
lock = threading.Lock()

js_file = read_json(instruction_file)

class DetectData(object):
    """detecdata"""
    def __init__(self, frame_data, detect_results):
        self.frame_data = frame_data
        self.detect_results = detect_results

class Postprocess(object): 
    """post"""
    def __init__(self, detect_model, device_id):
        self._detector = detect_model
        self._channel = None         
        self._data_queue =  queue.Queue(15)
        self._context = None
        self._start()
        self._exit = False
        self._process_time = 1

        # 20240128@cmx: device_id
        self._device_id = device_id

    def _start(self):
        # creat a thread and put func in the thread
        thread_id, ret = acl.util.start_thread(self._thread_entry, [])            
        utils.check_ret("acl.util.start_thread", ret)

    def _thread_entry(self, args_list):   
        # 20240128@cmx: device_id
        self._context, ret = acl.rt.create_context(self._device_id)
        utils.check_ret("acl.rt.create_context", ret)
        
        ret = True
        while ret: 
            if not self._data_queue.empty():
                with lock:
                    data = self._data_queue.get()
                    logger.text_log('第%d个npu，%s，正在进行功能性检验后处理' % (self._device_id, data.frame_data.ipcaddr))
                    print('第%d个npu，%s，正在进行功能性检验后处理' % (self._device_id, data.frame_data.ipcaddr))
                    if isinstance(data, DetectData):
                        try:
                            self._process_detect_data(data.detect_results, 
                                                            data.frame_data)
                        except:
                            ERROR = traceback.format_exc()
                            log_error(ERROR)
                            logger.error_log(ERROR)
                        logger.text_log('第%d个npu，%s，功能性检验后处理结束' % (self._device_id, data.frame_data.ipcaddr))
                        print('第%d个npu，%s，功能性检验后处理结束' % (self._device_id, data.frame_data.ipcaddr))
                    elif isinstance(data, str):
                        log_info("Post process thread exit")
                        self._exit = True
                        ret = False
                    else: 
                        log_error("post process thread receive unkonow data")   

            
    def _process_detect_data(self, detect_results, frame_data):
        self._detector.post_process(detect_results, frame_data)  
        ret = True                                                 
        return ret        

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
       
