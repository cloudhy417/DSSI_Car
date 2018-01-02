import serial
import time
import math
from datetime import datetime
import socket
import json
import syslog,time,sys
import RPi.GPIO as G
encoderPosR_prev=0
encoderPosL_prev=0
encoderPosR=0
encoderPosL=0
right_A=11
right_B=12
left_A=15
left_B=16
#interrupt function
G.setmode(G.BOARD)
G.setup(right_B,G.IN,pull_up_down=G.PUD_UP)
G.setup(left_B,G.IN,pull_up_down=G.PUD_UP)
def right_encoder(channel):
    G.setmode(G.BOARD)
    global encoderPosR
    if G.input(right_B):
        encoderPosR-=1
    else:
        encoderPosR+=1        
def left_encoder(channel):
    G.setmode(G.BOARD)
    global encoderPosL
    if G.input(left_B):
        encoderPosL+=1
    else:
        encoderPosL-=1
#interrupt setup
G.setup(right_A,G.IN,pull_up_down=G.PUD_DOWN)
G.add_event_detect(right_A, G.RISING, callback=right_encoder)
G.setup(left_A ,G.IN,pull_up_down=G.PUD_UP)
G.add_event_detect(left_A, G.RISING, callback=left_encoder)
#pwm output setup
pwmR_negative=22
pwmR_positive=18
pwmL_negative=36
pwmL_positive=32
G.setup(pwmR_positive, G.OUT)
pwmRp = G.PWM(pwmR_positive, 500)#freq=500Hz
pwmRp.start(1)
G.setup(pwmR_negative, G.OUT)
pwmRn = G.PWM(pwmR_negative, 500)#freq=500Hz
pwmRn.start(1)
G.setup(pwmL_positive, G.OUT)
pwmLp = G.PWM(pwmL_positive, 500)#freq=500Hz
pwmLp.start(1)
G.setup(pwmR_negative, G.OUT)
pwmLn = G.PWM(pwmR_negative, 500)#freq=500Hz
pwmLn.start(1)
#net setup
UDP_IP = "192.168.137.46"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))
time.sleep(1)
#parameter setup
radius=3.45
encoderNum=374
pwm_R = 1
pwm_L = 1
RL_factor_R=-0.5
RL_factor_L=0.3
posX=24
posY=24
pathX=[posX]
pathY=[posY]
pi=math.pi
head_Ang=pi/2
ang_Dif=0
dis_Dif=0
foward=True
T=0
N=90
#setup path
for i in range(1,46):
    pathX.append(23.5+i)
    pathY.append(0.0035*math.pow((23.5+i-47),3)+69)
for i in range(0, 46):
    pathX.append(69-i)
    pathY.append(-0.0035*math.pow((69-i-47), 3) + 157.5)
print pathX
print pathY
try:
    while True:
        data,addr = sock.recvfrom(1024)
        comma = data.index(".")
        period = data.index(",")
        print data[0:comma],"XXXXXXXXXXXXX",data[comma+1:period]
        posX = int(data[0:comma])
        posY = int(data[comma+1:period])
    #pwm algorithm
        encoderPosR_Inc=encoderPosR-encoderPosR_prev
        encoderPosL_Inc=encoderPosL-encoderPosL_prev
    #calculate head_Ang
        RL_encoder_diff=encoderPosR-encoderPosL
        arc_L=RL_encoder_diff*radius*2*pi/encoderNum
        head_Ang=pi/2+arc_L/17
        while head_Ang>2*pi:
            head_Ang-=2*pi
        while head_Ang<0:
            head_Ang+=2*pi
    #calculate position
        '''    
        encoder_Dist=(encoderPosR_Inc+encoderPosL_Inc)/2
        dist=encoder_Dist*radius*2*pi/encoderNum
        posX+=dist*math.cos(head_Ang)
        posY+=dist*math.sin(head_Ang)
        '''
    # error function
        x_Dif=pathX[T]-posX
        y_Dif=pathY[T]-posY    
        target_Ang=math.atan2(y_Dif,x_Dif)
        ang_Dif=target_Ang-head_Ang
        if ang_Dif>pi:
            ang_Dif=2*pi-ang_Dif
        if ang_Dif<-1*pi:
            ang_Dif=ang_Dif+2*pi
        dis_Dif=math.sqrt(math.pow(x_Dif,2)+math.pow(y_Dif,2))

        print encoderPosL," ",encoderPosR,"--------",head_Ang," X=",posX," Y=",posY
        print 'y_Dif=',y_Dif,'x_Dif=',x_Dif,'ang_Dif=',ang_Dif,'dis_Dif=',dis_Dif
    #perpendicular line
    
    #move to next target
        if dis_Dif<5:
            T+=4
        if y_Dif<0:
            T+=4
        if T>N:
            T=N
        print T
        
    #change from go foward to go backword
    #sign of kp_Dis should change
    #sign of kp_Ang remain

        if foward:
            sign=1
        else:
            sign=-1

        #kp_DisR=sign*0.1
        #kp_DisL=sign*0.1
        kp_AngR=10
        kp_AngL=-10
    # make pwm normalized
        if True:
            pwm_Control=sign*50
            pwm_DeadZone=sign*30
            pwm_R=pwm_DeadZone+dis_Dif*kp_DisR+ang_Dif*kp_AngR
            pwm_L=pwm_DeadZone+dis_Dif*kp_DisL+ang_Dif*kp_AngL
        print pwm_L,'-----',pwm_R
        '''
            if pwm_Rrate>pwm_Lrate:
                pwm_R=pwm_DeadZone+pwm_Control
                pwm_L=pwm_DeadZone+int(pwm_Control*(pwm_Lrate/pwm_Rrate))
            else:
                pwm_L=pwm_DeadZone+pwm_Control
                pwm_R=pwm_DeadZone+int(pwm_Control*(pwm_Rrate/pwm_Lrate))
        '''
    ##################
        if pwm_R > 255:
            pwm_R = 255
        if pwm_R != 0:
            if pwm_R<pwm_DeadZone:
                pwm_R=pwm_DeadZone
        if pwm_L > 255: 
            pwm_L = 255
        if pwm_L != 0:
            if pwm_L<pwm_DeadZone:
                pwm_L=pwm_DeadZone
    #write PWM value to arduino 
        pwm_R=pwm_R*100.0/255
        pwm_L=pwm_L*100.0/255
        if pwm_R>0: 
            pwmRp.ChangeDutyCycle(pwm_R)
        else:
            pwmRn.ChangeDutyCycle(pwm_R)
        if pwm_L>0:    
            pwmLp.ChangeDutyCycle(pwm_L)
        else:    
            pwmLn.ChangeDutyCycle(pwm_L)
        encoderPosR_prev=encoderPosR
        encoderPosL_prev=encoderPosL
        time.sleep(0.03)
        #port.write([chr(3),chr(pwm_R),chr(pwm_L)])
        start_flag=chr(0)
except KeyboardInterrupt:
        pass
finally:
        pwmRp.stop()
        pwmRn.stop()
        pwmLp.stop()
        pwmLn.stop()  
        G.cleanup()
