from time import strftime
from time import localtime
import sys
import os

#generate the name of output file
date = strftime('%Y%m%d_%H%M%S', localtime())
output_name = 'output' + date + '.txt'
output_name = 'output.txt'
f = open(output_name, 'w')

x = []
y = []
p1 = []
p2 = []

for i in range(0, 99):
    x.append(i)
    y.append(pow(i, 0.5))

for i in range(0, 99):
    f.write('(' + str(x[i]) + ', ' + str(y[i]) + ')\n')

f.close()
g = open(output_name, 'r')
print(g.read())
checkIfSave = str(raw_input('Do U want to save the recorded file?'))

if ((checkIfSave == 'Y') | (checkIfSave == 'y') | (checkIfSave == '1')):
    print('saved')
else:
    os.remove(output_name)
    print('deleted')
