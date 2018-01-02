import serial
import time
from datetime import datetime
port = serial.Serial("/dev/ttyS0",115200)#GPIO : ttyS0 #USB :ttyACM0
start_flag=chr(0)
encoderPosR = 0
encoderPosL = 0
pwm_R = 50
pwm_L = 50
RL_factor_R=-0.5
RL_factor_L=0.3
while True:
    #wait to start reading
    #timeCount = 10
    while ord(start_flag)!=3:
        start_flag = port.read()
        #timeCount=timeCount-1
    #read right encoder value
    highbyte = port.read()
    lowbyte = port.read()
    encoderPosR = ord(highbyte)*256+ord(lowbyte) 
    #read left encoder value
    highbyte = port.read()
    lowbyte = port.read()
    encoderPosL = ord(highbyte)*256+ord(lowbyte)
    #rTime=ord(port.read())
    #time=str(datetime.now())
    #time=(time[len(time)-5:len(time)-3])
    print encoderPosR," ",encoderPosL#,"aaaaaaaa",rTime,"---",time
    #write PWM value to arduino
    if True:
        RL_encoder_diff = encoderPosR - encoderPosL
      
        pwm_R = 50 + int( RL_encoder_diff * RL_factor_R )
        pwm_L = 47 + int( RL_encoder_diff * RL_factor_L )

    if (pwm_R > 250):
        pwm_R = 250
    #if (pwm_R < set_speed) pwm_R = set_speed;
    if (pwm_L > 250): 
        pwm_L = 250
    #if (pwm_L < set_speed) pwm_L = set_speed;
    #time =int(time)
    time.sleep(0.01)
    port.write([chr(3),chr(pwm_R),chr(pwm_L)])
    start_flag=chr(0)
