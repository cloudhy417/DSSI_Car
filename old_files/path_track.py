import serial
import time
import math
from datetime import datetime
port = serial.Serial("/dev/ttyS0",115200)#GPIO : ttyS0 #USB :ttyACM0
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
posX=24
posY=24
pathX=[posX]
pathY=[posY]
pi=math.pi
theta=pi/2
ang_Dif=0
dis_Dif=0
foward=True
T=0
N=95
for i in range(1,49):
    pathX.append(24+i)
    pathY.append(0.0035*math.pow((24+i-47),3)+69)
for i in range(0, 48):
    pathX.append(72-i)
    pathY.append(-0.0035 * math.pow((72-i-47), 3) + 157.5)
print len(pathX),'dcytkvulbinoktxjcygkvhubjlk'
print pathX
print pathY
while True:
    timeoutCount=5000
    timeout=False
    #wait to start reading
    while ord(start_flag)!=3 and timeoutCount>0:
        if port.in_waiting:    
            start_flag = port.read()
        timeoutCount-=1
        #print ord(start_flag)
    if timeoutCount is 0:
        timeout=True
        timeoutCount=5000
    if timeout is False:
    #read right encoder value
        highbyte = port.read()
        lowbyte = port.read()
        encoderPosR = ord(highbyte)*256+ord(lowbyte) 
    #read left encoder value
        highbyte = port.read()
        lowbyte = port.read()
        encoderPosL = ord(highbyte)*256+ord(lowbyte)
    else:
        encoderPosR=encoderPosR
        encoderPosL=encoderPosL

    sysime=str(datetime.now())
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
    print 'y_Dif=',y_Dif,'x_Dif=',x_Dif,'ang_Dif=',ang_Dif
    dis_Dif=math.sqrt(math.pow(x_Dif,2)+math.pow(y_Dif,2))
    #move to next target
    if dis_Dif<5:
        T+=2
    if y_Dif<0:
        T+=4
    if T>N:
        T=N
    print T

    if abs(x_Dif)<1e-8:
        if y_Dif>0:
            ang_Dif=theta-pi/2
        else:
            ang_Dif=theta-pi*3/2
    else:
        ang_Dif=math.atan2(y_Dif,x_Dif)-theta
    #
    if ang_Dif>pi:
        ang_Dif=2*pi-ang_Dif
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print encoderPosL," ",encoderPosR,"--------",theta," X=",posX," Y=",posY   
    #change from go foward to go backword
    #sign of kp_Dis should change
    #sign of kp_Ang remain

    if foward:
        sign=1
    else:
        sign=-1
    kp_DisR=sign*0.1
    kp_DisL=sign*0.1
    kp_AngR=2.4
    kp_AngL=-10
    # if close enough to the target position
    #if math.sqrt(math.pow(target_X_Dif,2)+math.pow(target_Y_Dif,2))<10:
    print math.sqrt(math.pow(x_Dif,2)+math.pow(y_Dif,2))
    #    pwm_R=0
    #    pwm_L=0
    #else:
    # make pwm normalized
    if True:
        pwm_Control=sign*50
        pwm_DeadZone=sign*21
        pwm_Rrate=dis_Dif*kp_DisR+ang_Dif*kp_AngR
        pwm_Lrate=dis_Dif*kp_DisL+ang_Dif*kp_AngL
        if pwm_Rrate>pwm_Lrate:
            pwm_R=pwm_DeadZone+pwm_Control
            pwm_L=pwm_DeadZone+int(pwm_Control*(pwm_Lrate/pwm_Rrate))
        else:
            pwm_L=pwm_DeadZone+pwm_Control
            pwm_R=pwm_DeadZone+int(pwm_Control*(pwm_Rrate/pwm_Lrate))

    ##################
    if pwm_R > 120:
        pwm_R = 120
    if pwm_R != 0:
        if pwm_R<pwm_DeadZone:
            pwm_R=pwm_DeadZone
    if pwm_L > 120: 
        pwm_L = 120
    if pwm_L != 0:
        if pwm_L<pwm_DeadZone:
            pwm_L=pwm_DeadZone
    #write PWM value to arduino 
    encoderPosR_prev=encoderPosR
    encoderPosL_prev=encoderPosL
    time.sleep(0.03)
    print pwm_L,'-----',pwm_R

    port.write([chr(3),chr(pwm_R),chr(pwm_L)])
    start_flag=chr(0)
    #print str(datetime.now())
