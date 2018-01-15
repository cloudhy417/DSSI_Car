import socket, threading, time, os
import time


HOST = ''
PORT = 5487
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',PORT))
s.listen(10)
conn, addr = s.accept()
try:
    while(1):
        b = conn.recv(1024)
        print(list(b))
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    s.close()
