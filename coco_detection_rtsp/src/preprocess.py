"""preprocess"""
import acl
import videocapture as video
import acllite_utils as utils
from acllite_imageproc import AclLiteImageProc
from acllite_logger import log_error, log_info

import time
# 20240314@xjk: path, logging class, post
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
                 resized_image, frame, ipcaddr):
        
        self.channel = rtsp_channel

        self.frame = frame
        self.frame_width = width
        self.frame_height = height

        self.resized_image = resized_image
        self.bgr_image = None
        # 20240331@xjk: ipcaddr
        self.ipcaddr = ipcaddr

class Preprocess(object): 
    """preprocess"""
    def __init__(self, stream_name, channel, resize_width, resize_height, device_id):
        self._stream_name = str(stream_name)
        self._channel = int(channel) 
        # 20240331@xjk: ipcaddr
        try:
            self._ipcaddr = js_file["camera"]["Camera"][self._channel]["IPCAddr"]
        except:
            ERROR = traceback.format_exc()
            print(ERROR)
            logger.error_log(ERROR)

        self._resize_width = resize_width
        self._resize_height = resize_height

        self._status = STATUS_PREPROC_INIT
        self._dvpp = None
        self._cap = None
        self._context = None

        self._device_id = device_id

        # 20240314@xjk: data
        self._image_put = None
        self._image_cat_put = None

        self._put_time = 1
        self._camera_restart_time = 0

    def _start(self):
        # creat a thread and put func in the thread
        thread_id, ret = acl.util.start_thread(self._thread_entry, [])            
        utils.check_ret("acl.util.start_thread", ret)

        log_info("Start sub thread ok, wait init...")
        while self._status == STATUS_PREPROC_INIT:
            time.sleep(0.001)
        log_info("Status changed to ", self._status)
        
        while self._status == STATUS_PREPROC_RUNNING:
            if self._image_put is not None or self._image_cat_put is not None:
                break
            time.sleep(0.001)
        
        return self._status != STATUS_PREPROC_ERROR


    def _thread_entry(self, args_list):
        #OD:20231103@cmx:send video status to control
        if self._stream_name is not None:
            dic_camera = {'camera':'status of %s 正常运行' % self._stream_name}
            print('======%s is ok !!!!!!======' % self._stream_name)
            post_camera_mess(dic_camera)

        # 20240314@cmx: device_id
        self._context, ret = acl.rt.create_context(self._device_id)
        utils.check_ret("acl.rt.create_context", ret)

        # get video according to ip, get class, similar to sentence, cap = cv2.VideoCapture(video_path)
        try:
            self._cap = video.VideoCapture(self._stream_name)
        except:
            ERROR = 'Error: Failed to open camera %s' % self._stream_name
            print(ERROR)
            logger.error_log(ERROR)

        self._dvpp = AclLiteImageProc() 
        self._status = STATUS_PREPROC_RUNNING
        

        # count frame
        frame_cnt = 0
        while self._status == STATUS_PREPROC_RUNNING: 
            # be similar to success, frame = cap.read()
            ret, image = self._cap.read()
            with lock:
                if ret:
                    log_error("Video %s decode failed" % (self._stream_name))
                    # 20240314@xjk: max restart time
                    self._camera_restart_time += 1
                    if self._camera_restart_time >= 10:
                        print('======  %s has restarted 10 time, stopping !!!!!!======' % self._stream_name)
                        logger.error_log('%s has restarted 10 time, stopping' % self._stream_name)
                        dic_camera = {'camera':'status of %s exception, stopping!!!' % self._stream_name}
                        post_camera_mess(dic_camera)
                        time.sleep(600)
                        print('======  %s restart !!!!!!======' % self._stream_name)
                        logger.text_log('%s restart' % self._stream_name)
                        dic_camera = {'camera':'status of %s restart !!!' % self._stream_name}
                        post_camera_mess(dic_camera)

                    # restart the camera
                    if self._cap:
                        self._cap.destroy()
                    self._cap = video.VideoCapture(self._stream_name)
                    ret, image = self._cap.read()
                    self._status = STATUS_PREPROC_RUNNING
            with lock:
                if (image is None) and self._cap.is_finished():
                    log_info("Video %s decode finish" % (self._stream_name)) 
                    # 20240314@xjk: max restart time
                    self._camera_restart_time += 1
                    if self._camera_restart_time >= 10:
                        print('======  %s has restarted 10 time, stopping !!!!!!======' % self._stream_name)
                        logger.error_log('%s has restarted 10 time, stopping' % self._stream_name)
                        dic_camera = {'camera':'status of %s exception, stopping!!!' % self._stream_name}
                        post_camera_mess(dic_camera)
                        time.sleep(600)
                        print('======  %s restart !!!!!!======' % self._stream_name)
                        logger.text_log('%s restart' % self._stream_name)
                        dic_camera = {'camera':'status of %s restart !!!' % self._stream_name}
                        post_camera_mess(dic_camera)
            
                    # restart the camera
                    if self._cap:
                        self._cap.destroy()
                    self._cap = video.VideoCapture(self._stream_name)
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
                    print(ERROR)
                    logger.error_log(ERROR)


        self._thread_exit()        

    def _process_frame(self, frame):
        # 20240314@xjk: log
        logger.text_log('第%d个npu，%s，解码完成，正在对图片进行预处理' % (self._device_id, self._ipcaddr))
        # 20240314@xjk: reduce camera_restart_time
        with lock:
            if self._put_time % 200 == 0 and self._camera_restart_time > 0:
                self._camera_restart_time -= 1
            self._put_time += 1
        
        # 20240314@xjk: preprocess
        resized_image = self._dvpp.crop_and_paste(frame, frame.width, frame.height, 
                                                self._resize_width, self._resize_height)
        print("=====log21=====")
        if resized_image is None:
            log_error("dvpp resize image failed")
            return
        # 20240331@xjk: ipcaddr
        data = PreProcData(self._channel, frame.width, frame.height, 
                        resized_image, frame, self._ipcaddr) 
             
        # 20240314@xjk: put data        
        self._image_put = data
        self._image_cat_put = data
        print("=====log27=====")
        logger.text_log('第%d个npu，%s，图片预处理完成' % (self._device_id, self._ipcaddr))


    def _thread_exit(self):
        self._status = STATUS_PREPROC_EXIT
        log_info("Channel %s thread exit..." % (self._ipcaddr))
        if self._dvpp is not None:
            del self._dvpp
            self._dvpp = None

        if self._cap is not None:
            while self._cap._dextory_dvpp_flag == False:
                time.sleep(0.001)
            del self._cap
            self._cap = None

        if self._context is not None:
            acl.rt.destroy_context(self._context)
            self._context = None
        log_info("Channel %s thread exit ok" % (self._ipcaddr))

    def set_display(self, display):
        """set display"""
        self._display = display

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
                log_error("decode channel %s failed" % (self._channel))
                return False, None
        
        if self._image_put is None:
            return True, None
        preproc_data = self._image_put
        self._image_put = None
        logger.text_log('第%d个npu，%s，功能性检测取图片成功' % (self._device_id,self._ipcaddr))
        return True, preproc_data 
    
    # 20240314@xjk: get car data
    def get_car_data(self):
        """
        The method for getting data 
        """
        if self._status >= STATUS_PREPROC_EXIT:            
            return False, None
        elif self._status == STATUS_PREPROC_INIT:
            ret = self._start()
            if ret == False:
                log_error("decode channel %s failed" % (self._channel))
                return False, None
        
        if self._image_cat_put is None:
            return True, None        
        preproc_data = self._image_cat_put
        self._image_cat_put = None
        logger.text_log('第%d个npu，%s，车辆车牌检测推理程序取图片成功' % (self._device_id,self._ipcaddr))
        return True, preproc_data 

    def __del__(self):
        self._thread_exit()


