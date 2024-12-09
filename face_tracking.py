import cv2
import numpy as np
from djitellopy import Tello
import time
from collections import deque

me = Tello()
me.connect()
print(me.get_battery())

me.streamon()
me.takeoff()
me.move_up(40)
me.send_rc_control(0, 0, 25, 0)
time.sleep(2.2)

w, h = 360, 240
fbRange = [6200, 6800]

pid = [0.4, 0.4, 0.002]
px_error = 0
py_error = 0

def findFace(img):
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListC = []
    myFaceListArea = []
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]

x_error_queue = deque(maxlen=100)
y_error_queue = deque(maxlen=100)

def trackFace(info, w, pid, px_error, py_error):
    area = info[1]
    x, y = info[0]

    x_error = x - w // 2
    y_error = y - h // 2

    x_speed = pid[0] * x_error + pid[1] * (x_error - px_error) + pid[2] * sum(x_error_queue)
    # x_speed = int(np.clip(x_speed, -100, 100))

    y_speed = pid[0] * y_error + pid[1] * (y_error - py_error) + pid[2] * sum(y_error_queue)
    # y_speed = int(np.clip(-y_speed, -100, 100))

    if area >= fbRange[0] and area <= fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20
    else:
        fb = 0

    if x == 0 or y == 0:
        x_error = 0
        y_error = 0
        x_speed = 0
        y_speed = 0
    
    x_error_queue.append(x_error)
    y_error_queue.append(y_error)

    print(f"fb={fb} x_speed={x_speed} y_speed={y_speed}")
    me.send_rc_control(0, fb, y_speed, x_speed)
    return x_error, y_error


while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w, h))
    img, info = findFace(img)
    px_error, py_error = trackFace(info, w, pid, px_error, py_error)
    cv2.imshow("Output", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        me.land()
        break
