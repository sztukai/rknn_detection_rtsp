"""preprocess"""
import cv2
import time
from util.message import *

import traceback
import threading
lock = threading.Lock()

STATUS_PREPROC_INIT = 1
STATUS_PREPROC_RUNNING = 2
STATUS_PREPROC_EXIT = 3
STATUS_PREPROC_ERROR = 4

js_file = read_json(instruction_file)

class PreProcData(object):
    """preprocdata"""
    def __init__(self, rtsp_channel, width, height, 
                 frame, ipcaddr):
        
        self.channel = rtsp_channel

        self.frame = frame
        self.frame_width = width
        self.frame_height = height

        self.input_img = None
        # 20240331@xjk: ipcaddr
        self.ipcaddr = ipcaddr

class Preprocess(object): 
    """preprocess"""
    def __init__(self, stream_name, channel, resize_height):
        self._stream_name = str(stream_name)
        self._channel = int(channel) 
        # 20240331@xjk: ipcaddr
        try:
            self._ipcaddr = js_file["camera"]["Camera"][self._channel]["IPCAddr"]
        except:
            ERROR = traceback.format_exc()
            logger.error_log(ERROR)

        self._resize_height = resize_height

        self._status = STATUS_PREPROC_INIT
        self._cap = None

        # 20240314@xjk: data
        self._image_put = None
        
        # 20240314@xjk: restart time
        self._put_time = 1
        self._camera_restart_time = 0

    def _start(self):
        # creat a thread and put func in the thread
        thread = threading.Thread(self._thread_entry, [])            
        thread.start()

        logger.text_log("Start sub thread ok, wait init...")
        while self._status == STATUS_PREPROC_INIT:
            time.sleep(0.001)
        logger.text_log("Status changed to ", self._status)
        
        while self._status == STATUS_PREPROC_RUNNING:
            if self._image_put is not None:
                break
            time.sleep(0.001)
        return self._status != STATUS_PREPROC_ERROR


    def _thread_entry(self, args_list):
        #OD:20231103@cmx:send video status to control
        if self._stream_name is not None:
            dic_camera = {'camera':'status of %s 正常运行' % self._stream_name}
            print('======%s is ok !!!!!!======' % self._stream_name)
            post_camera_mess(dic_camera)
        try:
            self._cap = cv2.VideoCapture(self._stream_name)
        except:
            ERROR = 'Error: Failed to open camera %s' % self._stream_name
            logger.error_log(ERROR)

        self._status = STATUS_PREPROC_RUNNING
    
        # count frame
        frame_cnt = 0
        while self._status == STATUS_PREPROC_RUNNING: 
            # be similar to success, frame = cap.read()
            ret, image = self._cap.read()
            if ret:
                logger.error_log("Video %s decode failed" % (self._stream_name))
                # 20240314@xjk: max restart time
                self._camera_restart_time += 1
                if self._camera_restart_time >= 10:
                    logger.error_log('%s has restarted 10 time, stopping' % self._stream_name)
                    dic_camera = {'camera':'status of %s exception, stopping!!!' % self._stream_name}
                    post_camera_mess(dic_camera)
                    time.sleep(600)
                    logger.text_log('%s restart' % self._stream_name)
                    dic_camera = {'camera':'status of %s restart !!!' % self._stream_name}
                    post_camera_mess(dic_camera)

                # restart the camera
                if self._cap:
                    self._cap.release()
                self._cap = cv2.VideoCapture(self._stream_name)
                ret, image = self._cap.read()
                self._status = STATUS_PREPROC_RUNNING
            if (image is None) and self._cap.is_finished():
                logger.text_log("Video %s decode finish" % (self._stream_name)) 
                # 20240314@xjk: max restart time
                self._camera_restart_time += 1
                if self._camera_restart_time >= 10:
                    logger.error_log('%s has restarted 10 time, stopping' % self._stream_name)
                    dic_camera = {'camera':'status of %s exception, stopping!!!' % self._stream_name}
                    post_camera_mess(dic_camera)
                    time.sleep(600)
                    logger.text_log('%s restart' % self._stream_name)
                    dic_camera = {'camera':'status of %s restart !!!' % self._stream_name}
                    post_camera_mess(dic_camera)
        
                # restart the camera
                if self._cap:
                    self._cap.release()
                self._cap = cv2.VideoCapture(self._stream_name)
                ret, image = self._cap.read()
                self._status = STATUS_PREPROC_RUNNING
            try:
                if image and (int(frame_cnt) % 25 == 0):
                        print('=====log20=====')
                        self._process_frame(image)
                        frame_cnt = 1 
                    
                frame_cnt += 1
            except:
                    ERROR = traceback.format_exc()
                    logger.error_log(ERROR)


        self._thread_exit()        

    def _process_frame(self, frame):
        # 20240314@xjk: log
        logger.text_log('%s，解码完成，正在对图片进行预处理' % (self._ipcaddr))
        # 20240314@xjk: reduce camera_restart_time
        with lock:
            if self._put_time % 200 == 0 and self._camera_restart_time > 0:
                self._camera_restart_time -= 1
            self._put_time += 1
    
        # 20240331@xjk: ipcaddr
        data = PreProcData(self._channel, frame.width, frame.height, 
                        frame, self._ipcaddr) 
             
        # 20240314@xjk: put data        
        self._image_put = data
        print("=====log27=====")
        logger.text_log('%s，图片预处理完成' % (self._ipcaddr))


    def _thread_exit(self):
        self._status = STATUS_PREPROC_EXIT
        logger.text_log("Channel %s thread exit..." % (self._ipcaddr))

        if self._cap is not None:
            self.cap.release()
            self._cap = None

        logger.text_log("Channel %s thread exit ok" % (self._ipcaddr))


    def is_finished(self):
        """
        Function description:
            Judge whether the process is completed
        Parameter:
            none
        Return Value:
            True or Fal
        Exception Description:
            none
        """
        return self._status > STATUS_PREPROC_RUNNING
    
    def get_data(self):
        """
        The method for getting data 
        """
        if self._status >= STATUS_PREPROC_EXIT:            
            return False, None
        elif self._status == STATUS_PREPROC_INIT:
            ret = self._start()
            if ret == False:
                logger.error_log("decode channel %s failed" % (self._channel))
                return False, None
        
        if self._image_put is None:
            return True, None
        preproc_data = self._image_put
        self._image_put = None
        logger.text_log('第%d个npu，%s，功能性检测取图片成功' % (self._device_id,self._ipcaddr))
        return True, preproc_data 
    
    def __del__(self):
        self._thread_exit()


