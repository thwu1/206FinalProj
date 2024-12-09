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
me.send_rc_control(0, 0, 25, 0)

w, h = 960, 720
fbRange = [6200, 6800]

pid = [0.2, 0.04, 0.005]

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
# in_camera = deque(maxlen=50)

# for _ in range(50):
#     in_camera.append(1)

# p_ls = []
# i_ls = []
# d_ls = []

center_coords_queue = deque(maxlen=20)
TURN = ["+"]

def trackFace(info, w, pid, px_error, py_error):
    area = info[1]
    x, y = info[0]

    center_coords_queue.append((x, y))
    if x != 0 or y != 0:
        if x < w // 2:
            TURN[0] = "-"
        else:
            TURN[0] = "+"
    # print(x)
    x_error = x - w // 2
    y_error = y - h // 4

    if x == 0 or y == 0:
        x_error = 0
        y_error = 0
    
    print(x,y)
    print(x_error, y_error)

    x_speed = (
        pid[0] * x_error + pid[1] * (x_error - px_error) + pid[2] * sum(x_error_queue)
    )
    # p_ls.append(pid[0] * x_error)
    # i_ls.append(pid[2] * sum(x_error_queue))
    # d_ls.append(pid[1] * (x_error - px_error))

    x_speed = int(np.clip(x_speed, -100, 100))

    y_speed = (
        pid[0] * y_error + pid[1] * (y_error - py_error) + pid[2] * sum(y_error_queue)
    )
    y_speed = int(np.clip(-0.5 * y_speed, -40, 40))

    if area >= fbRange[0] and area <= fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20
    else:
        fb = 0

    if me.get_height() > 220:
        me.send_rc_control(0, 0, -10, 0)

    if x == 0 or y == 0:
        if sum([1 for x, y in center_coords_queue if x == 0 and y == 0]) > 15:
            # print(TURN[0])
            # pass
            if TURN[0] == "+":
                me.send_rc_control(0, 0, 0, 40)
            else:
                me.send_rc_control(0, 0, 0, -40)
        else:
            me.send_rc_control(0, 0, 0, 0)

        x_error = 0
        y_error = 0
        x_speed = 0
        y_speed = 0
    else:
        me.send_rc_control(0, fb, y_speed, x_speed)

    x_error_queue.append(x_error)
    y_error_queue.append(y_error)

    time.sleep(0.1)

    print(f"fb={fb} x_speed={x_speed} y_speed={y_speed}")
    return x_error, y_error

px_error = 0
py_error = 0

while True:
    img = me.get_frame_read().frame
    # print(f"Image shape: {img.shape}")  # Will print height, width, channels
    # img = cv2.resize(img, (w, h))
    img, info = findFace(img)
    px_error, py_error = trackFace(info, w, pid, px_error, py_error)
    cv2.imshow("Output", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        me.land()
        break

# import matplotlib.pyplot as plt

# plt.hist(p_ls, label="p")
# plt.hist(i_ls, label="i")
# plt.hist(d_ls, label="d")

# print(p_ls[-100:], i_ls[-100:], d_ls[-100:])
# plt.legend()
# plt.show()