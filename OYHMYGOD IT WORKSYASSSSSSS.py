import cv2
import numpy as np
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time
from libcamera import Transform
import os

panServo = 4
tiltServo = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(panServo, GPIO.OUT)
GPIO.setup(tiltServo, GPIO.OUT)

def positionServo(servo, angle):
    os.system("python angleServoCtrl.py " + str(servo) + " " + str(angle))

def mapServoPosition(x, y):
    global panAngle
    global tiltAngle

    if (x > 220):
        panAngle += 5 
        if panAngle > 140:
            panAngle = 140
        positionServo(panServo, panAngle)

    if (x < 280):
        panAngle -= 5 
        if panAngle < 40:
            panAngle = 40
        positionServo(panServo, panAngle)

    if (y > 160):
        tiltAngle += 5 
        if tiltAngle > 140:
            tiltAngle = 140
        positionServo(tiltServo, tiltAngle)

    if (y < 210):
        tiltAngle -= 5  
        if tiltAngle < 40:
            tiltAngle = 40
        positionServo(tiltServo, tiltAngle)

ballz_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (500, 350),},transform=Transform(vflip=1)))
picam2.start()

global panAngle
panAngle = 90
global tiltAngle
tiltAngle = 90

positionServo(panServo, panAngle)
positionServo(tiltServo, tiltAngle)

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

        
        if distance < 50:
            continue

        mapServoPosition(int(center_x), int(center_y))

    cv2.imshow("Camera", im)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()