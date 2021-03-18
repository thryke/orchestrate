import os
# test = os.path.join(os.getcwd(),"../../..","point.txt")
# print(test)
f = open("../../point.txt", "r")
point = f.read()
f.close()

print(point)