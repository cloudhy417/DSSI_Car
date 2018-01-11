pathX=[posX]
pathY=[posY]

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
    pathY.append(-0.001 * math.pow((69 - i - 47),3) - 0.5 * (69 - i - 47) + 157.5)
	
for i in range(0,6):
    pathX.append(23.5)
    pathY.append(180 + 5*i)
	
for i in range(0,16):
    pathX.append(23.5)
    pathY.append(205 - 7.6*i)
	
for i in range(0,45):
    pathX.append(25 + i)
    pathY.append(-0.001 * math.pow((25 + i - 47),3) - 0.5 * (25 + i - 47) + 69)
	
for i in range(1,6):
    pathX.append(23.5)
    pathY.append(69 - 4.6*i)
	

N=len(pathX)-1
print pathX,' ',len(pathX)
print pathY,' ',len(pathY)