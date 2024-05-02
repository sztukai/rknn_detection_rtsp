# 20230811@cmx
import json
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
    pass
        
def post_camera_mess(data):
    pass