#!/usr/bin/python3

# program made solely for the purpose of counting valid compartments in model

from model import Model	# ./model.py

# load model blueprint as Model
model = Model()

modelX = model.dataX	# model diameter. should be odd
modelY = model.dataY	# model diameter. should be odd
modelZ = model.dataZ	# model height.

count = 0
for z in range(modelZ):
	for x in range(modelX):
		for y in range(modelY):
			# is this coordinate valid? ask Model
			if not(model.exists(x,y,z)):
				continue
			count = count + 1


print("TOTAL COMPARTMENT NUMBERRRRRRRRRR".center(40))
print("*"*40)
print(str(count).center(40))
print("*"*40)






