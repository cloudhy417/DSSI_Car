import RPi.GPIO as GPIO

b = 12
b = input('which GPIO?\n')


GPIO.setmode(GPIO.BOARD)
GPIO.setup(b, GPIO.OUT)
pwm = GPIO.PWM(b, 500)
pwm.start(1)

try:
    while 1:
        a = input('Duty%=')
        if (a > 0):
            pwm.ChangeDutyCycle(a)
        elif (a < 0):
            break
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()

    
