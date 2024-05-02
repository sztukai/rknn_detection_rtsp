import cv2

font_scale = 1.0  
font_thickness = 2  
font = cv2.FONT_HERSHEY_SIMPLEX  

#TODO:20230910@qyx: anchor boxes
def anchor_v3(image_post, label, lt_x, lt_y, rb_x, rb_y):
    label_size, _ = cv2.getTextSize(label, font, font_scale, font_thickness)
    rect_width = label_size[0] + 10
    rect_height = label_size[1] + 10

    cv2.rectangle(image_post, (lt_x, lt_y), (rb_x, rb_y), (255, 0, 0), 3)
    # 20240415#xjk
    # cv2.rectangle(image_post, (lt_x, lt_y - 20 + 5), (lt_x + rect_width, lt_y + rect_height), (0, 0, 255), -1)
    cv2.rectangle(image_post, (lt_x, lt_y - rect_height), (lt_x + rect_width, lt_y), (0, 0, 255), -1)
    # cv2.putText(image_post, label, (lt_x, lt_y + label_size[1] + 5), font, font_scale, (255, 255, 255), font_thickness)
    cv2.putText(image_post, label, (lt_x, lt_y), font, font_scale, (255, 255, 255), font_thickness)

    print("==============anchors==============")

    return image_post