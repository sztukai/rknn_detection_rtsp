import cv2
import numpy as np

# TODO:20231020@cmx: color  
def color(img, lt_x, lt_y, rb_x, rb_y):
    print("=====log60=====")
    img_2 = img[lt_x:rb_x, lt_y:rb_y]
    print("=====log60-1=====")
    if img_2 is None:
        print("======error=====")
    else:    
        hsv = cv2.cvtColor(img_2, cv2.COLOR_BGR2HSV)

        print("=====long61=====")
        lower_blue = np.array([8, 10, 30])
        upper_blue = np.array([130, 255, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        blue_pixels = cv2.countNonZero(mask)
        print("=====log62=====")
        if blue_pixels > img_2.shape[0] * img_2.shape[1] / 2:
            print("=====log63=====")
            return True
        else:
            print("=====log64=====")
            return False

