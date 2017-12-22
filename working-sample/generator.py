#!/usr/bin/python3

from model import Model	# ./model.py

# load model blueprint as Model
model = Model()
#model.show()	# just checkin'.

modelX = model.dataX	# model diameter. should be odd
modelY = model.dataY	# model diameter. should be odd
modelZ = model.dataZ	# model height.

for z in range(modelZ):
	for x in range(modelX):
		for y in range(modelY):
			# is this coordinate valid? ask Model
			if not(model.exists(x,y,z)):
				continue
			# print info of compartment
			print("{:4d} {:4d} {:4d}\t0 3f 0 0 0.0".format(x-int(modelX/2), y-int(modelY/2), z-int(modelZ/2)) )

			# print associated reactions
			print(model.reactionFlags(x,y,z))


model.printConcentration()







