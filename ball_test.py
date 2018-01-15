import serial
import time
import math
from datetime import datetime
import socket
import json
import syslog,time,sys
import RPi.GPIO as G
from thread import *

G.setmode(G.BOARD)

#pwm output setup
pwm_1 = 38
pwm_2 = 40

G.setup(pwm_1, G.OUT)
pwm1 = G.PWM(pwm_1, 50)#freq=50Hz
pwm1.start(1)
G.setup(pwm_2, G.OUT)
pwm2 = G.PWM(pwm_2, 50)#freq=50Hz
pwm2.start(1)


pwm1.ChangeDutyCycle(7.5)
pwm2.ChangeDutyCycle(7.5)

try:
    while True:
	
        pwm1.ChangeDutyCycle(13)
        time.sleep(0.8)
        pwm1.ChangeDutyCycle(7.5)
        time.sleep(0.8)
        pwm2.ChangeDutyCycle(13)
        time.sleep(0.8) 
        pwm2.ChangeDutyCycle(7.5)
        time.sleep(0.8)

        time.sleep(5)

        pwm1.ChangeDutyCycle(13)
        time.sleep(0.8)
        pwm1.ChangeDutyCycle(7.5)
        time.sleep(0.8)
        pwm2.ChangeDutyCycle(3)
        time.sleep(0.8) 
        pwm2.ChangeDutyCycle(7.5)
        time.sleep(0.8)

        time.sleep(5)
       
except KeyboardInterrupt:
    pass
finally:
    pwm1.stop()
    pwm2.stop()
    G.cleanup()
