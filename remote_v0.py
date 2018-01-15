import serial
import time
import math
from datetime import datetime
import socket
import json
import syslog,time,sys
import RPi.GPIO as G
from thread import *




encoderPosR_prev=0
encoderPosL_prev=0
encoderPosR=0
encoderPosL=0
right_A=11
right_B=12
left_A=15
left_B=16
motor_pin = 33
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
G.setup(pwmL_negative, G.OUT)
pwmLn = G.PWM(pwmL_negative, 500)#freq=500Hz
pwmLn.start(1)
G.setup(motor_pin, G.OUT)
#net setup
UDP_IP = "192.168.137.59"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#sock.bind((UDP_IP,UDP_PORT))
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
N=141
sumX = 0
sumY = 0

#setup path
'''
for i in range(1,46):
    pathX.append(23.5+i)
    pathY.append(0.0035*math.pow((23.5+i-47),3)+69)
for i in range(0, 46):
    pathX.append(69-i)
    pathY.append(-0.0035*math.pow((69-i-47), 3) + 157.5)
for i in range(1,6):
    pathX.append(23.5)
    pathY.append(200-20*i)
for i in range(0,46):
    pathX.append(69-(46-i))
    pathY.append(-0.0035*math.pow((69-(46-i)-47), 3) + 69)
'''
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
        HOST_phone = ''
        PORT_phone = 1111

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c = 0
        global input_x
        global input_y
        global motor
        input_x=0
        input_y=0
        motor = 0
        print 'Socket created'

        #try:
        s.bind((HOST_phone,PORT_phone))
        #except socket.error , msg:
        #    print 'Bind failed. Eror Code: '+str(msg[0]+' Message '+msg[1]
        #    sys.exit()

        print 'Socket bind complete'

        s.listen(10)
        print 'Socket now listening'

        def clientthread(conn,c):
            conn.send('Welcome to the server. Receiving Data...\n')

            while True:
                data = conn.recv(1024)
                cmd = list(data)
                reply = 'Message Recerived at the server!\n'
                for i in range (0,len(data)):
                    if c==0:
                        print 'motor'
                        print ord(cmd[i])
                        global motor
                        motor = ord(cmd[i])
                    elif c==1:
                        print 'x'
                        print ord(cmd[i])
                        global input_x
                        input_x=ord(cmd[i])
                    elif c==2:
                        print 'y'
                        print ord(cmd[i])
                        global input_y
                        input_y=ord(cmd[i])
                    c+=1

                if not data:
                    break

                conn.sendall(reply)
            conn.close()

        while 1:

            c = 0
            conn, addr = s.accept()
            print 'Connect with ' +addr[0]+':'+str(addr[1])
            print '\n'
            #sumY = (sumY + 0.8 * input_y) / 1.8
            sumY = input_y

            if(sumY >= 100):
                pwm_R=( (sumY-100) - 0.5*(input_x-100) )*0.8
                pwm_L=( (sumY-100) + 0.5*(input_x-100) )*0.8
            else:
                pwm_R=( (sumY-100) + 0.5*(input_x-100) )*0.8
                pwm_L=( (sumY-100) - 0.5*(input_x-100) )*0.8
            


            if(pwm_R > 99):
                pwm_R = 99
            if(pwm_L > 99):
                pwm_L = 99
            if(pwm_R < -99):
                pwm_R = -99
            if(pwm_L < -99):
                pwm_L = -99

            if(motor > 100):
                G.output(motor_pin, 1)
            else:
                G.output(motor_pin, 0)

            
            if(abs(pwm_L) < 5):
                pwm_L = 0
            if(abs(pwm_R) < 5):
                pwm_R = 0

            if pwm_R>0: 
                pwmRp.ChangeDutyCycle(pwm_R)
                pwmRn.ChangeDutyCycle(0)
            else:
                pwmRn.ChangeDutyCycle((-1*pwm_R))
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
            start_new_thread(clientthread,(conn,c))

        s.close()

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
        
except KeyboardInterrupt:
    pass
finally:
    pwmRp.stop()
    pwmRn.stop()
    pwmLp.stop()
    pwmLn.stop()  
    G.cleanup()
