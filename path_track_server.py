import soclet
import serial
import json
import syslog,time,sys
import time
import math
from datetime import datetime


port = serial.Serial("/dev/ttyS0",115200)#GPIO : ttyS0 #USB :ttyACM0

UDP_IP = "192.168.43.102"
UDP_PORT = 5006
sock = socket.socket(socket.AF_INET,
		     socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))
time.sleep(1)

start_flag=chr(0)
encoderPosR_prev=0
encoderPosL_prev=0
encoderPosR = 0
encoderPosL = 0
radius=3.45
encoderNum=374
pwm_R = 1
pwm_L = 1
RL_factor_R=-0.5
RL_factor_L=0.3
pathX=[0]
pathY=[0]
posX=0
posY=0
pi=math.pi
theta=pi/2
ang_Dif=0
dis_Dif=0
T=0
N=10000

for i in range(1,N):
    pathX.append(0)
    pathY.append(0.01*i)
	
while True:
    #timeoutCount=5000
    #timeout=False
    #wait to start reading
    #while ord(start_flag)!=3 and timeoutCount>0:
    #    if port.in_waiting:    
    #        start_flag = port.read()
    #    timeoutCount-=1
    #    #print ord(start_flag)
    #if timeoutCount is 0:
    #    timeout=True
    #    timeoutCount=5000
    #if timeout is False:
    ##read right encoder value
    #    highbyte = port.read()
    #    lowbyte = port.read()
    #    encoderPosR = ord(highbyte)*256+ord(lowbyte) 
    ##read left encoder value
    #    highbyte = port.read()
    #    lowbyte = port.read()
    #    encoderPosL = ord(highbyte)*256+ord(lowbyte)
    #else:
    #    encoderPosR=encoderPosR
    #    encoderPosL=encoderPosL

    sysime=str(datetime.now())
	
    data,addr = sock.recvfrom(1024)
    comma = data.index(",")
    period = data.index(".")
    x = int(data[0:comma])
    y = int(data[comma+1:period])
	
	
    #pwm algorithm

    encoderPosR_Inc=encoderPosR-encoderPosR_prev
    encoderPosL_Inc=encoderPosL-encoderPosL_prev
    #calculate theta
    RL_encoder_diff=encoderPosR-encoderPosL
    arc_L=RL_encoder_diff*radius*2*pi/encoderNum
    theta=pi/2+arc_L/17
    #calculate position
    encoder_Dist=(encoderPosR_Inc+encoderPosL_Inc)/2
    dist=encoder_Dist*radius*2*pi/encoderNum
    posX+=dist*math.cos(theta)
    posY+=dist*math.sin(theta)
    if theta>2*pi:
        theta=0
    if theta<0:
        theta+=2*pi
    # error function
    x_Dif=pathX[T]-posX
    y_Dif=pathY[T]-posY    
    T+=10
    if T>=10000:
        T=9999
    print T
    dis_Dif=math.sqrt(math.pow(x_Dif,2)+math.pow(y_Dif,2))
    if abs(x_Dif)<1e-8:
        ang_Dif=theta-pi/2
    else:
        ang_Dif=theta-math.atan(1.0*y_Dif/x_Dif)
    print encoderPosL," ",encoderPosR,"--------",theta," X=",posX," Y=",posY   
    kp_DisR=0.1
    kp_DisL=0.1
    kp_AngR=-10
    kp_AngL=10
    target_X_Dif=pathX[9999]-posX
    target_Y_Dif=pathY[9999]-posY
    if math.sqrt(math.pow(target_X_Dif,2)+math.pow(target_Y_Dif,2))<10:
        print math.sqrt(math.pow(target_X_Dif,2)+math.pow(target_Y_Dif,2))
        pwm_R=0
        pwm_L=0
    else:
        pwm_Base=30
        pwm_Rrate=dis_Dif*kp_DisR+ang_Dif*kp_AngR
        pwm_Lrate=dis_Dif*kp_DisL+ang_Dif*kp_AngL
        if abs(pwm_Rrate)<1e-3 or abs(pwm_Lrate<1e-3):
            pwm_Rrate=1
            pwm_Lrate=1
        if pwm_Rrate>pwm_Lrate:
            pwm_R=20+pwm_Base
            pwm_L=20+int(pwm_Base*(pwm_Lrate/pwm_Rrate))
        else:
            pwm_L=20+pwm_Base
            pwm_R=20+int(pwm_Base*(pwm_Rrate/pwm_Lrate))

    ##################
    if pwm_R > 250:
        pwm_R = 250
    if pwm_R != 0:
        if pwm_R<25:
            pwm_R=25
    if pwm_L > 250: 
        pwm_L = 250
    if pwm_L != 0:
        if pwm_L<25:
            pwm_L=25
    #write PWM value to arduino 
    encoderPosR_prev=encoderPosR
    encoderPosL_prev=encoderPosL
    time.sleep(0.03)
    print pwm_L,'-----',pwm_R
    port.write([chr(3),chr(pwm_R),chr(pwm_L)])
    start_flag=chr(0)
    #print str(datetime.now())
