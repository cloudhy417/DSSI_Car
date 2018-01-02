import math
c='c'
pwm=ord(c)*10
print math.cos(1.57)
pathX=[0]
pathY=[0]
for i in range(1,10000):
    pathX.append(0)
    pathY.append(0.01*i)
print len(pathX)
print len(pathY)
