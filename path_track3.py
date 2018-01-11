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
pwmR_negative=22
pwmR_positive=18
pwmL_negative=36
pwmL_positive=32
stop=False
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
G.setup(pwmR_positive, G.OUT)
pwmRp = G.PWM(pwmR_positive, 500)#freq=500Hz
pwmRp.start(1)
G.setup(pwmR_negative, G.OUT)
pwmRn = G.PWM(pwmR_negative, 500)#freq=500Hz
pwmRn.start(1)
G.setup(pwmL_positive, G.OUT)
pwmLp = G.PWM(pwmL_positive, 500)#freq=500Hz
pwmLp.start(1)
G.setup(pwmL_negative, G.OUT)
pwmLn = G.PWM(pwmL_negative, 500)#freq=500Hz
pwmLn.start(1)
#net setup
UDP_IP = "192.168.137.149"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
#sock.bind((UDP_IP,UDP_PORT))
time.sleep(1)
#parameter setup
radius=3.45
encoderNum=374
pwm_R = 1
pwm_L = 1
RL_factor_R=-0.5
RL_factor_L=0.3
posX=22
posY=22
pathX=[23.5]
pathY=[23.5]
pi=math.pi
head_Ang=pi/2
ang_Dif=0
dis_Dif=0
foward=True
T=0

#setup path
for i in range(0,6):
    pathX.append(23.5)
    pathY.append(24 + 4.6*i)
	
for i in range(0,45):
    pathX.append(25 + i)
    pathY.append(0.001 * math.pow((25 + i - 47),3) + 0.5 * (25 + i - 47) + 69)
	
for i in range(0,6):
    pathX.append(69)
    pathY.append(91 + 8.8*i)
	
for i in range(0,45):
    pathX.append(69 - i)
    pathY.append(-0.001 * math.pow((69 - i - 52),3) - 0.5 * (69 - i - 47) + 157.5)

for i in range(0,6):
    pathX.append(30)
    pathY.append(180 + 5*i)
middle=len(pathX)
#print middle
for i in range(0,18):
    pathX.append(23.5)
    pathY.append(205 - 7.6*i)
	
for i in range(0,45):
    pathX.append(25 + i)
    pathY.append(-0.001 * math.pow((25 + i - 47),3) - 0.5 * (25 + i - 47) + 50)
	
for i in range(1,15):
    pathX.append(69)
    pathY.append(50 - 4.6*i)
	
N=len(pathX)-1
#print pathX,' ',len(pathX)
#print pathY,' ',len(pathY)
try:
    while True:
    #receive data
        '''
        data,addr = sock.recvfrom(1024)
        comma = data.index(".")
        period = data.index(",")
        print data[0:comma],"XXXXXXXXXXXXX",data[comma+1:period]
        posX = int(data[0:comma])
        posY = int(data[comma+1:period])
        '''
    #pwm algorithm
        encoderPosR_Inc=encoderPosR-encoderPosR_prev
        encoderPosL_Inc=encoderPosL-encoderPosL_prev
    #calculate head_Ang
        RL_encoder_diff=encoderPosR-encoderPosL
        arc_L=RL_encoder_diff*radius*2*pi/encoderNum
        head_Ang=pi/2+arc_L/17
        if not foward:
            head_Ang+=pi
        while head_Ang>2*pi:
            head_Ang-=2*pi
        while head_Ang<0:
            head_Ang+=2*pi
    #calculate position
         
        encoder_Dist=(encoderPosR_Inc+encoderPosL_Inc)/2
        dist=encoder_Dist*radius*2*pi/encoderNum
        if foward:
            posX+=dist*math.cos(head_Ang)
            posY+=dist*math.sin(head_Ang)
        else:
            posX-=dist*math.cos(head_Ang)
            posY-=dist*math.sin(head_Ang)
        
    #perpendicular line
    #y=mx+b ---> y-mx-b=0 m=-dx/dy 
        jump=2
        if T is not N:    
            dy=pathY[T+jump]-pathY[T]
            dx=pathX[T+jump]-pathX[T]
            m=-1.0*dx/dy
            b=pathY[T]-m*pathX[T]
    #move to next target
            posSide=posY-m*posX-b
            nextPointSide=pathY[T+1]-m*pathX[T+1]-b
        if T>=middle:
            foward=False
        if dis_Dif<3:
            T+=jump
        if T is not N:    
            if posSide*nextPointSide>0:
                T+=jump
        if T==N:
            T=N
            stop=True
        print T
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

        #print 'encL=',encoderPosL,"encR=",encoderPosR,"--------head_Ang=",head_Ang," X=",posX," Y=",posY
        #print 'y_Dif=',y_Dif,'x_Dif=',x_Dif,'ang_Dif=',ang_Dif,'dis_Dif=',dis_Dif
        
        #print 'posX=',posX,'posY=',posY,'  ','posXR=',posXR,'posYR=',posYR
    #change from go foward to go backword
    #sign of kp_Dis and kp_Ang should change

        if foward:
            sign=1
        else:
            sign=-1

        #kp_DisR=sign*0.1
        #kp_DisL=sign*0.1
        if foward:
            kp_AngR=22.2222
            kp_AngL=-33.3333
        else:
            kp_AngR=33.3333
            kp_AngL=-22.2222

    # compute pwm 
        if True:

            pwm_BaseSpeed=sign*(55.5555*math.cos(ang_Dif))
            pwm_R=pwm_BaseSpeed+ang_Dif*kp_AngR
            pwm_L=pwm_BaseSpeed+ang_Dif*kp_AngL
        print 'pwm_L=',pwm_L,'-----pwm_R=',pwm_R
        ''' 
            if pwm_Rrate>pwm_Lrate:
                pwm_R=pwm_DeadZone+pwm_Control
                pwm_L=pwm_DeadZone+int(pwm_Control*(pwm_Lrate/pwm_Rrate))
            else:
                pwm_L=pwm_DeadZone+pwm_Control
                pwm_R=pwm_DeadZone+int(pwm_Control*(pwm_Rrate/pwm_Lrate))
        '''
    ##################
        pwm_DeadZone=sign*0
        if pwm_R>0:
            if pwm_R > 255:
                pwm_R = 255
            if pwm_R != 0:
                if pwm_R<pwm_DeadZone:
                    pwm_R=0
        else:
            if pwm_R < -255:
                pwm_R = -255
            if pwm_R != 0:
                if pwm_R>pwm_DeadZone:
                    pwm_R=0
        if pwm_L>0:
            if pwm_L > 255: 
                pwm_L = 255
            if pwm_L != 0:
                if pwm_L<pwm_DeadZone:
                    pwm_L=0
        else:
            if pwm_L < -255: 
                pwm_L = -255
            if pwm_L != 0:
                if pwm_L>pwm_DeadZone:
                    pwm_L=0

    #write PWM value to GPIO 
        if stop:
            pwm_R=0
            pwm_L=0
        pwm_R=pwm_R*100.0/255
        pwm_L=pwm_L*100.0/255
        if pwm_R>0: 
            pwmRp.ChangeDutyCycle(pwm_R)
            pwmRn.ChangeDutyCycle(0)
        else:
            pwmRn.ChangeDutyCycle(-1*pwm_R)
            pwmRp.ChangeDutyCycle(0)
        if pwm_L>0:    
            pwmLp.ChangeDutyCycle(pwm_L)
            pwmLn.ChangeDutyCycle(0)
        else:
            pwmLn.ChangeDutyCycle(-1*pwm_L)  
            pwmLp.ChangeDutyCycle(0)
        encoderPosR_prev=encoderPosR
        encoderPosL_prev=encoderPosL
        time.sleep(0.01)
except KeyboardInterrupt:
        pass
finally:
        pwmRp.stop()
        pwmRn.stop()
        pwmLp.stop()
        pwmLn.stop()  
        G.cleanup()
