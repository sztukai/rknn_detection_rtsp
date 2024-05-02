# 20230811@cmx
import json
import requests
import base64
import traceback
from util.tools import TextLogger

# 20240314@xjk: path
aiimg = '/opt/xdiot/xdexchange/aiimg/'
log_location = "/opt/xdiot/xdexchange/ailog/"
Json_log_location = "/opt/xdiot/xdexchange/json_log/"
instruction_file = '/opt/xdiot/xdexchange/conf/camera.json'
logger = TextLogger(log_location)
Json_logger = TextLogger(Json_log_location, Logger_name='Json_log')

def read_json(instruction_file):
    js_file = json.load(open(instruction_file, encoding='utf-8'))
    return js_file

def post_mess(data):
    try:
        # 20240123@cmx: dynamic api according to host
        js_file = read_json(instruction_file)
        cur = js_file["camera"]["ApiUrl"]
        requests.post(cur, json=data, headers={"Content-Type": "application/json"},timeout=1)
        Json_logger.text_log(str(data))
    except:
        ERROR = traceback.format_exc()
        print(ERROR)
        Json_logger.error_log(ERROR)
        
def post_camera_mess(data):
    try:
        # 20240123@cmx: dynamic api according to host
        js_file = read_json(instruction_file)
        cur = 'http://'+js_file["camera"]["DeviceAddr"]+':6060/api/start/records'
        requests.post(cur, json=data, headers={"Content-Type": "application/json"},timeout=1)
        Json_logger.text_log(str(data))
    except:
        ERROR = traceback.format_exc()
        print(ERROR)
        Json_logger.error_log(ERROR)

def convert_image_to_base64(image_path):  
    with open(image_path, 'rb') as image_file: 
        return base64.b64encode(image_file.read()).decode('utf-8')  
    
def color_convert(st):
    shorts = {
        '黑色': 5,
        "蓝色": 2,
        "绿色": 5,
        "白色": 5,
        "黄色": 5
    }
    return shorts.get(st, None)





