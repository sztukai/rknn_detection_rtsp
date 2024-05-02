from util.message import *

js_file = read_json(instruction_file)

def fire_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):
    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 

    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":js_file["alarm"]["fire"]["code"],
            "CapType":'',
            "CapId":'',
            "DriveIntoStatus":'',
            "AlarmId":'',
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":'',
            "EventNum":'',
            "PlateReliability":score,
            "PlateColor":'',
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log41=====")

def work_clothe_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):
    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":js_file["alarm"]["workclothes"]["code"],
            "CapType":0,
            "CapId":11111111111,
            "DriveIntoStatus":0,
            "AlarmId":11111111111,
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":"AAAAAA",
            "EventNum":5,
            "PlateReliability":score,
            "PlateColor":2,
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log42=====")


def smoke_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):
    
    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":'9',
            "CapType":0,
            "CapId":11111111111,
            "DriveIntoStatus":0,
            "AlarmId":11111111111,
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":"AAAAAA",
            "EventNum":5,
            "PlateReliability":score,
            "PlateColor":2,
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log43=====")


def person_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):

    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":js_file["alarm"]["intrusion"]["code"],
            "CapType":'',
            "CapId":'',
            "DriveIntoStatus":'',
            "AlarmId":'',
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":'',
            "EventNum":'',
            "PlateReliability":score,
            "PlateColor":'',
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log44=====")

def lost_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):

    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":js_file["alarm"]["lost"]["code"],
            "CapType":0,
            "CapId":11111111111,
            "DriveIntoStatus":0,
            "AlarmId":11111111111,
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":"AAAAAA",
            "EventNum":5,
            "PlateReliability":score,
            "PlateColor":2,
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log45=====")

def waste_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):

    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":js_file["alarm"]["waste"]["code"],
            "CapType":'',
            "CapId":'',
            "DriveIntoStatus":'',
            "AlarmId":'',
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":"AAAAAA",
            "EventNum":'',
            "PlateReliability":score,
            "PlateColor":'',
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log46=====")


def car_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score, ocr_word, color):

    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)

    dic2 = js_file['camera']['Camera'][channel]

    dic1.update(dic2)

    dic3 = {
            "AlarmType":999,
            "CapType":'',
            "CapId":'',
            "DriveIntoStatus":'',
            "AlarmId":'',
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":save_path,
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x ,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":ocr_word,
            "EventNum":'',
            "PlateReliability":score,
            "PlateColor":color,
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    
    post_mess(dic1)
    print("=====log48=====")

def parkingspace_post(channel, current_time_str, save_path, lt_x, lt_y, rb_x, rb_y, score):

    key_list = list(js_file['camera'].keys())
    keys_to_get1 = ['SerialNumber','AreaId']
    keys_to_get3 = ['SerialNumber','AreaId','Camera']    
    keys_to_get2 = [key for key in key_list if key not in keys_to_get3] 
    dic1 = {key: js_file['camera'][key] for key in keys_to_get1}
    dic4 = {key: js_file['camera'][key] for key in keys_to_get2}

    dic1.update(dic4)
    dic2 = js_file['camera']['Camera'][channel]
    dic1.update(dic2)
    dic3 = {
            "AlarmType":js_file["alarm"]["parkingspace"]["code"],
            "CapType":'',
            "CapId":'',
            "DriveIntoStatus":'',
            "AlarmId":'',
            "Timestamp":current_time_str,
            "BigImageURL":save_path,
            "BigImage":{
                    "ImageType":"jpg",
                    "Image":''
                        },
            "PlateImageURL":"",
            "PlateImage":{
                    "ImageType":"jpg",
                    "Image":""
                },
            "LeftTopX":lt_x,
            "LeftTopY":lt_y,
            "RightBtmX":rb_x,
            "RightBtmY":rb_y,
            "PlateNO":'',
            "EventNum":'',
            "PlateReliability":score,
            "PlateColor":'',
            "PlateType":0,
            "ReportRate":60,
            }

    dic1.update(dic3)
    post_mess(dic1)
    
    print("=====log49=====")