
data = "22,9."

comma = data.index(",")
period = data.index(".")

x = int(data[0:comma])
y = int(data[comma+1:period])


print(x)
print("---")
print(y)
