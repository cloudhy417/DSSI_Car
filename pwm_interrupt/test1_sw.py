import RPi.GPIO as G
import time

G.setmode(G.BOARD)
G.setup(8, G.IN, pull_up_down=G.PUD_DOWN)

a = 1

try:
    while(a == 1):
        if G.input(8):
            print('Hi\n')
        else:
            print('Low\n')
        time.sleep(1)
except KeyboardInterrupt:
    a = 0
    pass
finally:
    G.cleanup()
