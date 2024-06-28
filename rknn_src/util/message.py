# 20230811@cmx
import json
import traceback

import requests
from util.tools import TextLogger

# 20240314@xjk: path
aiimg = '/opt/xdiot/xdexchange/aiimg/' 
log_location = "/opt/xdiot/xdexchange/ailog/" # 输出log
Json_log_location = "/opt/xdiot/xdexchange/json_log/" # 上位机log
instruction_file = '/opt/xdiot/xdexchange/conf/camera.json' # 配置文件

logger = TextLogger(log_location)
Json_logger = TextLogger(Json_log_location, Logger_name='Json_log')


def read_json(instruction_file):
    js_file = json.load(open(instruction_file, encoding='utf-8'))
    return js_file
js_file = read_json(instruction_file)

def post_mess(data):
    try:
        # 20240123@cmx: dynamic api according to host
        cur = js_file["apiurl"]
        Json_logger.text_log(str(data))
        requests.post(cur, json=data, headers={"Content-Type": "application/json"},timeout=1)
    except:
        ERROR = traceback.format_exc()
        logger.error_log(ERROR)
        
def post_camera_mess(data):
    pass

def fire_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):
    dic = {
            "event_id": 'fire' + current_time_str + str(score),
            "event_type": 'fire',
            "event_time": current_time_str,
            "x1": lt_x,
            "y1": lt_y,
            "x2": rb_x,
            "y2": rb_y,
            "reliability": score,
            "image_path": save_path,
            "camera_ip": js_file['camera'][channel]['ip'],
            "ch_id": js_file['camera'][channel]['ch'],
            "plate_no": None,
            "event_num": 1,
            "ext": None,
            }
    post_mess(dic)
    print("=====log48=====")

def smoke_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):              
    dic = {
            "event_id": 'smoke' + current_time_str + str(score),
            "event_type": 'smoke',
            "event_time": current_time_str,
            "x1": lt_x,
            "y1": lt_y,
            "x2": rb_x,
            "y2": rb_y,
            "reliability": score,
            "image_path": save_path,
            "camera_ip": js_file['camera'][channel]['ip'],
            "ch_id": js_file['camera'][channel]['ch'],
            "plate_no": None,
            "event_num": 1,
            "ext": None,
            }
    post_mess(dic)
    print("=====log49=====")

def intrusion_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):
    dic = {
            "event_id": 'intrusion' + current_time_str + str(score),
            "event_type": 'intrusion',
            "event_time": current_time_str,
            "x1": lt_x,
            "y1": lt_y,
            "x2": rb_x,
            "y2": rb_y,
            "reliability": score,
            "image_path": save_path,
            "camera_ip": js_file['camera'][channel]['ip'],
            "ch_id": js_file['camera'][channel]['ch'],
            "plate_no": None,
            "event_num": 1,
            "ext": None,
            }
    post_mess(dic)
    print("=====log50=====")
