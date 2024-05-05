# 20230811@cmx
import json
import traceback
from util.tools import TextLogger

# 20240314@xjk: path
aiimg = './aiimg/'
log_location = "./ailog/"
Json_log_location = "./json_log/"
instruction_file = './camera.json'
logger = TextLogger(log_location)
Json_logger = TextLogger(Json_log_location, Logger_name='Json_log')

def read_json(instruction_file):
    js_file = json.load(open(instruction_file, encoding='utf-8'))
    return js_file

def post_mess(data):
    pass
        
def post_camera_mess(data):
    pass