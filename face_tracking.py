import cv2
import numpy as np
from djitellopy import Tello
import time
from collections import deque
import pickle

me = Tello()
me.connect()
print(me.get_battery())

me.streamon()
me.takeoff()
me.send_rc_control(0, 0, 25, 0)

w, h = 960, 720
fbRange = [14000, 15000]

pid = [0.2, 0.04, 0.005]
INDEX = 0

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

def circle_motion(drone, speed, yaw_speed, duration):
    """
    Perform a circular motion with the Tello drone.

    Args:
        drone (Tello): The Tello drone instance.
        speed (int): Linear speed in cm/s.
        yaw_speed (int): Yaw rotation speed in degrees per second.
        duration (int): Duration of the motion in seconds.
    """
    print(f"Starting circular motion with speed={speed} cm/s, yaw_speed={yaw_speed} deg/s, and duration={duration} seconds")

    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            # Check if "q" is pressed to stop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[DEBUG] 'q' pressed, stopping and landing...")
                break

            # Send RC control commands: move forward and yaw
            drone.send_rc_control(speed, 0, 0, yaw_speed)
            time.sleep(0.05)  # Maintain smooth control by sending commands frequently

    except Exception as e:
        print(f"[ERROR] An error occurred during circular motion: {e}")

    finally:
        # Stop the motion
        print("[DEBUG] Stopping drone...")
        drone.send_rc_control(0, 0, 0, 0)
        time.sleep(0.1)
        
    # # Example usage of circle_motion in main:
    # circle_motion(me, speed=-30, yaw_speed=-35, duration=24)  # Adjust speed, yaw speed, and duration as needed

def read_sensor_and_perform_action():
    with open("cache.pkl", "rb") as file:
        allSnaps = pickle.load(file)
    global INDEX
    if len(allSnaps)>INDEX:
        print("current command:", allSnaps[INDEX])
        Command = allSnaps[INDEX]
        INDEX +=1
        execute_command(Command)

def execute_command(command):
    print("executing command:", command)
    if command == 1:
        print("Yield to circle motion")
        circle_motion(me, speed=-30, yaw_speed=20, duration=24)
        print("Circle motion done")
    else:
        pass

px_error = 0
py_error = 0

while True:
    img = me.get_frame_read().frame
    img, info = findFace(img)
    px_error, py_error = trackFace(info, w, pid, px_error, py_error)
    read_sensor_and_perform_action()
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