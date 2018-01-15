import serial
import time
import math
from datetime import datetime
import socket
import json
import syslog,time,sys
import RPi.GPIO as G
from thread import *
import threading
import multiprocessing


G.setmode(G.BOARD)

#pwm output setup
pwm_switch = 38
pwm_split = 40
pwm_shoot = 35
pwm_shoot2 = 31
pwm_release = 37
global split_last
global shoot_last
global release_last
global split
global shoot
global release
global split_state
global shoot_state

split_last = 0
shoot_last = 0
split = 0
shoot = 0
split_state = 0
shoot_state = 0

G.setup(pwm_switch, G.OUT)
pwmswitch = G.PWM(pwm_switch, 50)#freq=50Hz
pwmswitch.start(1)
G.setup(pwm_split, G.OUT)
pwmsplit = G.PWM(pwm_split, 50)#freq=50Hz
pwmsplit.start(1)
G.setup(pwm_shoot, G.OUT)
pwmshoot = G.PWM(pwm_shoot, 50000)#freq=50Hz
pwmshoot.start(1)
G.setup(pwm_release, G.OUT)
pwmrelease = G.PWM(pwm_release, 50)#freq=50Hz
pwmrelease.start(1)
G.setup(pwm_shoot2, G.OUT)
pwmshoot2 = G.PWM(pwm_shoot2, 50000)#freq=50Hz
pwmshoot2.start(1)


#net setup
#UDP_IP = "192.168.137.59"
#sock.bind((UDP_IP,UDP_PORT))
time.sleep(0.05)

def	work_split():
    global split_state
    while(1):
        if split_state == 0:
            pwmswitch.ChangeDutyCycle(2)
            pwmsplit.ChangeDutyCycle(9)
        elif split_state == 1:
            pwmswitch.ChangeDutyCycle(4)
            time.sleep(0.5) 
            pwmswitch.ChangeDutyCycle(2)
            time.sleep(0.3)
            pwmsplit.ChangeDutyCycle(7)
            time.sleep(0.5)
            pwmsplit.ChangeDutyCycle(9)
            time.sleep(0.1)
            split_state = 0
        elif split_state == 2:
            pwmswitch.ChangeDutyCycle(4)
            time.sleep(0.5) 
            pwmswitch.ChangeDutyCycle(2)
            time.sleep(0.3)
            pwmsplit.ChangeDutyCycle(11)
            time.sleep(0.5)
            pwmsplit.ChangeDutyCycle(9)
            time.sleep(0.1)
            split_state = 0
        print ('thread=' + str(split_state))
        time.sleep(0.1)

def	work_shoot():
    global shoot_state
    while(1):
        if shoot_state == 0:
            pwmrelease.ChangeDutyCycle(9.5)
            pwmshoot.ChangeDutyCycle(0)
            pwmshoot2.ChangeDutyCycle(0)
        elif shoot_state == 1:
            pwmrelease.ChangeDutyCycle(13) 
            time.sleep(2.5)
            pwmrelease.ChangeDutyCycle(9.5)
            shoot_state = 0
            print('open')
        elif shoot_state == 2:
            
            
            pwmshoot2.ChangeDutyCycle(90)
            time.sleep(0.2)
            pwmshoot2.ChangeDutyCycle(0)

            pwmshoot.ChangeDutyCycle(90)
            time.sleep(0.35)
            shoot_state = 0
        time.sleep(0.05)
    


def clientthread(conn,c):
    global split
    global split_last
    global split_state

    global shoot
    global shoot_last
    conn.send('Welcome to the server. Receiving Data...\n')

    split_last = split
    shoot_last = shoot

    while True:
        data = conn.recv(1024)
        cmd = list(data)
        reply = 'Message Recerived at the server!\n'
        for i in range (0,len(data)):
            if c==0:
                '''
                print 'y'
                print ord(cmd[i])
                '''
            elif c==1:
                '''
                print 'split'
                print ord(cmd[i])
                '''
                split=ord(cmd[i]) - 100
            elif c==2:
                '''
                print 'shoot'
                print ord(cmd[i])
                '''
                shoot=ord(cmd[i]) - 100
            c+=1
        if not data:
            break
    conn.close()



#main
try:
    p1 = threading.Thread(target = work_split)
    p2 = threading.Thread(target = work_shoot)
    
    p1.setDaemon(True)
    p2.setDaemon(True)

    p1.start()
    p2.start()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        #receive data

        HOST_phone = ''
        PORT_phone = 5487
        
        c = 0

        print 'Socket created'
        s.bind((HOST_phone,PORT_phone))
        print 'Socket bind complete'
        s.listen(10)
        print 'Socket now listening'
        while 1:
            c = 0
            conn, addr = s.accept()
            print 'Connect with ' +addr[0]+':'+str(addr[1])
            print '\n'
							
            start_new_thread(clientthread,(conn,c))
            
            if(split > 70):
                if(split_state==0):
                    split_state = 1
            elif(split < -70):
                if(split_state==0):
                    split_state = 2
            else:
                pass


            if(shoot > 70):
                if(shoot_state==0):
                    shoot_state = 1
            elif(shoot < -70):
                if(shoot_state==0):
                    shoot_state = 2
            else:
                pass
            print ('recv=' + str(split_state))

        
       
except KeyboardInterrupt:
    pass
finally:
    s.close()
    pwmswitch.stop()
    pwmsplit.stop()
    pwmshoot.stop()
    pwmrelease.stop()
 
    G.cleanup()
