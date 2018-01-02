import RPi.GPIO as G


G.setmode(G.BOARD)
def my_callback_one(channel):
    if G.input(8):
        print('Rising Edge!')
    else:
        print('Falling Edge!')
#def my_callback_two(8):
#    print('Falling Edge!')


G.setup(8, G.IN, pull_up_down=G.PUD_DOWN)
G.add_event_detect(8, G.BOTH, callback=my_callback_one, bouncetime=200)
#G.add_event_callback(8, my_callback_one)

try:
    while 1:
        pass


except KeyboardInterrupt:
    pass
finally:
    G.cleanup()
