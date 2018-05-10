#!/usr/bin/python3

from model import Model	# ./model.py

# load model blueprint as Model
model = Model()
modelX = model.dataX	# model diameter. should be odd
modelY = model.dataY	# model diameter. should be odd
modelZ = model.dataZ	# model height.

output = []
for z in range(modelZ):
	cz = z-int(modelZ/2)
	for x in range(modelX):
		cx = x-int(modelX/2)
		for y in range(modelY):
			# is this coordinate valid?
			if not(model.exists(x,y,z)):
				continue
			# compartment parameters
			output.append( "{} {} {} 0 3f 0 0 0.0".format(cx, y-int(modelY/2), cz) )
			# associated reactions
			output.append( model.reactionFlags(x,y,z) )

print("\n".join(output))

model.printConcentration()
