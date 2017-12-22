
import json

class Model:

	def __init__(self):
		self.fi = open("blueprint.txt")
		self.model = []	# model[z][x][y]
		size = self.fi.readline().split()
		self.dataX = int(size[0])
		self.dataY = int(size[1])
		self.dataZ = int(size[2])
		for zscan in range(self.dataZ):
			self.fi.readline()	# skip comment line
			layer = []	# layer[x][y]. temporary data for appending to 'model'
			for line in range(self.dataX):
				line = self.fi.readline().strip()
				if(len(line)!=self.dataY):
					print("error: line length != dataY")
					exit()
				#print(line)
				layer.append(line.upper())
			self.model.append(layer)
		# load reaction group relationships
		self.tableSG = json.load(open("symbol-group.json"))
		self.tableGC = json.load(open("group-compartment.json"))
		# initial parameters & their names
		self.presets = []	
		self.names = []
		for x in json.load(open("concentration.json")):
			self.names.append(x[0])
			d = {}
			for pair in x[1]:
				d[pair.upper()] = x[1][pair]
			self.presets.append(d)

	# shows contents of 'model' for debugging
	def show(self):
		print("(x,y,z) = ({},{},{})".format(self.dataX,self.dataY,self.dataZ))
		for z in range(self.dataZ):
			for x in range(self.dataX):
				for y in range(self.dataY):
					print(self.model[z][x][y],end="")
				print("")
			print("")

	# prints symbol concentration of 'symbol' for all compartments
	def printConcentration(self):
		for symbol in range(len(self.presets)):
			print("// " + str(self.names[symbol]) )
			for z in range(self.dataZ):
				for x in range(self.dataX):
					for y in range(self.dataY):
						if not( self.exists(x,y,z) ):
							continue
						print( str(self.queryParameter(symbol,self.model[z][x][y])) +" ",end="" )
			print("")

	# return True  : compartment exists.
	# return False : void. no compartment exists here.
	def exists(self,x,y,z):
		return (self.model[z][x][y] != "_")
		pass

	# returns the reaction groups that a compartment is associated with as a string of 0 & 1s
	def reactionFlags(self,x,y,z):
		if(  self.model[z][x][y] == "P"): return "100000000001111000"	# plasma membrane
		elif(self.model[z][x][y] == "."): return "010000000100000000"	# cytosol
		elif(self.model[z][x][y] == "X"): return "001011111110000111"	# disc membrane
		elif(self.model[z][x][y] == "*"): return "001011111110000111"	# disc membrane w Luminopsin
		else                            : return "000000000000000000"	#(default reaction flags)

	# returns initial concentration of 'symbol' in compartments of type 'cmpType'
	def queryParameter(self,symbol,cmpType):
		# which reaction groups include 'symbol'?
		for reaction in [(hit) for hit in self.tableSG if hit[0]==symbol ]:
			# which compartments include the reaction group?
			for match in [(x) for x in self.tableGC if x[0]==reaction[2]]:
				# does the compartment type match the query?
				if(match[1] == cmpType):
					#return self.presets[symbol]
					if(cmpType.upper() in self.presets[symbol]): return self.presets[symbol][cmpType.upper()]
					else                                       : return self.presets[symbol]['DEFAULT']
		return 0.0




