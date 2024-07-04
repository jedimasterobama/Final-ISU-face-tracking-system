import cv2
import cv2.data
import numpy as np
from picamera2 import Picamera2
import gpiod
import time
from libcamera import Transform
import os

STEP_PIN = 17
DIR_PIN = 18
ENABLE_PIN = 23

STEP_PIN2 = 20
DIR_PIN2 = 21
ENABLE_PIN2 = 16

chip = gpiod.Chip('gpiochip4')

step_line = chip.get_line(STEP_PIN)
dir_line = chip.get_line(DIR_PIN)
enable_line = chip.get_line(ENABLE_PIN)

step2_line = chip.get_line(STEP_PIN2)
dir2_line = chip.get_line(DIR_PIN2)
enable2_line = chip.get_line(ENABLE_PIN2)

step_line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)
dir_line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)
enable_line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)

step2_line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)
dir2_line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)
enable2_line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)



def set_direction(clockwise=True):
    dir_line.set_value(1 if clockwise else 0)

def enable_motor(enable=True):
    enable_line.set_value(0 if enable else 1) 

def step(steps, delay=0.015):
    for _ in range(steps):
        step_line.set_value(1)
        time.sleep(delay)
        step_line.set_value(0)
        time.sleep(delay)

def set_direction2(clockwise=True):
    dir2_line.set_value(1 if clockwise else 0)

def enable_motor2(enable=True):
    enable2_line.set_value(0 if enable else 1)  

def step2(steps, delay=0.01):
    for _ in range(steps):
        step2_line.set_value(1)
        time.sleep(delay)
        step2_line.set_value(0)
        time.sleep(delay)

def mapsteps(x, y):
    diff_x = x - 250
    diff_y = y - 175
    
    print(diff_x, diff_y)
    
    if abs(diff_x) < 50:
            steps_x = abs(diff_x) // 12
            steps_y = abs(diff_y) // 15
            
    elif abs(diff_x) >= 50:
            steps_x = abs(diff_x) // 18
            steps_y = abs(diff_y) // 15
    
    
    if diff_x < 0:
        enable_motor(True)
        set_direction(False)  
        step(steps_x)
    elif diff_x > 0:
        enable_motor(True)
        set_direction(True)   
        step(steps_x)
    
    if diff_y > 0:
        enable_motor2(True)
        set_direction2(False)  
        step2(steps_y)
    elif diff_y < 0:
        set_direction2(True)   
        step2(steps_y)
        
    
    return steps_x, steps_y 

ballz_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (500, 350),},transform=Transform(vflip=1)))
picam2.start()


while True:
    im = picam2.capture_array()
    grey = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    faces = ballz_detector.detectMultiScale(grey, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0))

        center_x = x + w // 2
        center_y = y + h // 2
        cv2.circle(im, (center_x, center_y), 3, (0, 0, 255), -1)

        distance = np.sqrt((center_x - 250) ** 2 + (center_y - 175) ** 2)

        
        if distance < 10:
            
            continue
        steps_x, steps_y = mapsteps(center_x, center_y)

        

    cv2.imshow("littleboy", im)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
enable_motor(False)
enable_motor2(False)
cv2.destroyAllWindows()
step_line.release()
dir_line.release()
enable_line.release()
step2_line.release()
dir2_line.release()
enable2_line.release()