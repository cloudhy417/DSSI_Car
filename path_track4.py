import serial
import time
import math
from datetime import datetime
import socket
import json
import syslog,time,sys
import RPi.GPIO as G
port = serial.Serial("/dev/ttyS0",115200)#GPIO : ttyS0 #USB :ttyACM0
encoderPosR_prev=0
encoderPosL_prev=0
encoderPosR = 0
encoderPosL = 0
right_A=8
right_B=10
left_A=3
left_B=5
#interrupt function
def right_encoder(channel):
    if G.input(right_B):
        encoderPosR+=1
    else:
        encoderPosR-=1        
def left_encoder(channel):
    if G.input(left_B):
        encoderPosL+=1
    else:
        encoderPosL-=1
#interrupt setup
G.setmode(G.BOARD)
G.setup(right_A, G.IN, pull_up_down=G.PUD_DOWN)
G.add_event_detect(right_A, G.BOTH, callback=right_encoder, bouncetime=200)
G.setup(left_A, G.IN, pull_up_down=G.PUD_DOWN)
G.add_event_detect(left_A, G.BOTH, callback=right_encoder, bouncetime=200)
#pwm output setup
pwm_pin=15
G.setup(pwm_pin, G.OUT)
pwm = G.PWM(pwm_pin, 500)#freq=500Hz
#net setup
UDP_IP = "192.168.43.102"
UDP_PORT = 5006
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
#sock.bind((UDP_IP,UDP_PORT))
time.sleep(1)
#parameter setup
start_flag=chr(0)
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
N=95
#setup path
for i in range(1,49):
    pathX.append(24+i)
    pathY.append(0.0035*math.pow((24+i-47),3)+69)
for i in range(0, 48):
    pathX.append(72-i)
    pathY.append(-0.0035 * math.pow((72-i-47), 3) + 157.5)
print pathX
print pathY
try:
	while True:
		#data,addr = sock.recvfrom(1024)
		#comma = data.index(",")
		#period = data.index(".")
		#x = int(data[0:comma])
		#y = int(data[comma+1:period])
						
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
		#pwm algorithm

		encoderPosR_Inc=encoderPosR-encoderPosR_prev
		encoderPosL_Inc=encoderPosL-encoderPosL_prev
		#calculate head_Ang
		RL_encoder_diff=encoderPosR-encoderPosL
		arc_L=RL_encoder_diff*radius*2*pi/encoderNum
		head_Ang=pi/2+arc_L/17
		#calculate position
		encoder_Dist=(encoderPosR_Inc+encoderPosL_Inc)/2
		dist=encoder_Dist*radius*2*pi/encoderNum
		posX+=dist*math.cos(head_Ang)
		posY+=dist*math.sin(head_Ang)
		if head_Ang>2*pi:
			head_Ang=0
		if head_Ang<0:
			head_Ang+=2*pi
		# error function
		x_Dif=pathX[T]-posX
		y_Dif=pathY[T]-posY    
		target_Ang=math.atan2(y_Dif,x_Dif)
		ang_Dif=target_Ang-head_Ang
		if ang_Dif>pi:
			ang_Dif=2*pi-ang_Dif
		dis_Dif=math.sqrt(math.pow(x_Dif,2)+math.pow(y_Dif,2))

		print encoderPosL," ",encoderPosR,"--------",head_Ang," X=",posX," Y=",posY
		print 'y_Dif=',y_Dif,'x_Dif=',x_Dif,'ang_Dif=',ang_Dif,'dis_Dif=',dis_Dif
		#move to next target
		if dis_Dif<5:
			T+=2
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

		kp_DisR=sign*0.1
		kp_DisL=sign*0.1
		kp_AngR=2.4
		kp_AngL=-10
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
		print pwm_L,'-----',pwm_R
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
		port.write([chr(3),chr(pwm_R),chr(pwm_L)])
		start_flag=chr(0)
