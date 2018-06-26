
from struct import unpack

class CalFile:
	""" class for parsing a single .cal file

	==== functions ====
	__init__(filename)
	                a .cal file to open must be specified as string [filename].
	parseHeader()   initialize global variables. should be executed before other functions are called.
	printInfo()     print basic info, such as number of compartments, time steps, etc.
	getSequence(s,x,y,z)
	                returns concentration of symbol [s] in compartment at [x][y][z].

	==== variables ====
	f               file handler
	symbolNames     string list of all symbol names in simulation
	symbolUnits     string list of all symbol units, stored in same order as symbolNames
	symbolOut       string list of symbols recorded in file 
	timeStart       start time of simulation
	timeEnd         end time of simulation
	timeDelta       time step used in simulation
	timeRecord      time interval of records
	timeN           number of recorded timepoints
	cStatus         contains: number of compartments, number of membranes, compartment length X, Y, Z
	c               hashes c[(x,y,z)] => compartment ID. used in getSequence()
	offsetResults   binary offset of simulation results in .cal file
	verbose         when False, supresses trivial notifications except errors
	"""

	f = None
	symbolNames = []
	symbolUnits = []
	symbolOut = []
	timeStart = 0.0
	timeEnd = 0.0
	timeDelta = 0.0
	timeRecord = 0.0
	timeN = 0
	cStatus = []
	c = {}
	offsetResults = None
	verbose = False

	def __init__(self,filename=None,verbose=False):
		""" initialize. 'filename' must be specified
		"""
		try:
			self.f = open(filename,"rb")
		except OSError as e:
			print("could not open \"{}\"".format(filename))
			raise
		except:
			raise
		if(isinstance(verbose,bool)):
			self.verbose = verbose
		if(self.verbose):
			print("opening file: {}".format(filename))
		self.parseHeader()

	def parseHeader(self):
		""" extract basic information from self.f.
			this function is time-consuming, and is therefore separated.
		"""
		# length constants derived from Sim_prog.cpp
		LEN_HEADER = 160
		LEN_TAB = 16
		LEN_STRING = 512

		# irrelevant bytes
		self.f.seek(LEN_HEADER,0)

		# *Information****
		self.f.seek(LEN_TAB,1)
		size = int.from_bytes(self.f.read(4),byteorder="little")
		self.f.seek(size,1)

		# *VsimFile*******
		self.f.seek(LEN_TAB,1)
		self.f.seek(4+LEN_STRING,1)

		# *Symbol List****
		self.f.seek(LEN_TAB,1)
		n = int.from_bytes(self.f.read(4),byteorder="little")
		for i in range(n):
			size = int.from_bytes(self.f.read(4),byteorder="little")
			self.symbolNames.append(self.f.read(size).decode())
			size = int.from_bytes(self.f.read(4),byteorder="little")
			self.symbolUnits.append(self.f.read(size).decode())
			self.f.seek(4*5 + 8*7, 1)		# other symbol attributes

		# *CalcCondition**
		self.f.seek(LEN_TAB,1)
		(self.timeStart,self.timeEnd,self.timeDelta,self.timeRecord) = unpack("<dddd",self.f.read(32))		# start, end, calculation interval, output interval
		self.timeN = int( ((self.timeEnd - self.timeStart) / self.timeRecord) +1 )

		# *OutputSymbols**
		self.f.seek(LEN_TAB,1)
		n = int.from_bytes(self.f.read(4), byteorder="little")
		for i in range(n):
			size = int.from_bytes(self.f.read(4), byteorder="little")
			self.symbolOut.append( self.f.read(size).decode() )

		# *Stimulation****
		self.f.seek(LEN_TAB,1)
		n = int.from_bytes(self.f.read(4), byteorder="little")
		for i in range(n):
			# TODO: should ba able to handle cases with stimulation
			pass

		# *CompartmentSt.*
		self.f.seek(LEN_TAB,1)
		self.cStatus = unpack("<iiddd",self.f.read(8+24))		# compartments, membranes, compartment length X, Y, Z
		for i in range(self.cStatus[0]):
			self.c[ unpack("<iiiBii",self.f.read(21))[0:3] ] = i		# self.c[x,y,z] = i

		# *SymbolValues***
		# initial values.
		# TODO: should ba able to handle cases with N_TRANS, N_EXTRA, N_INTRA, etc.
		self.f.seek(LEN_TAB,1)
		self.f.seek(8 * self.cStatus[0] * len(self.symbolNames), 1)

		# *results********
		self.f.seek(LEN_TAB,1)
		self.offsetResults = self.f.tell()

		# file size validation
		self.f.seek(0,2)
		estimate = 8*self.cStatus[0]*len(self.symbolOut)*self.timeN + 4*self.timeN
		recordSize = self.f.tell() - self.offsetResults
		if( estimate > recordSize ):
			x = recordSize / (8*self.cStatus[0]*len(self.symbolOut) + 4)
			x = x-1		# because the first step is only the initial parameters
			if(self.verbose):
				print("actual file size is smaller than expected, found only {} steps (= {:.3f} s)".format(x, x*self.timeRecord))
			self.timeN = int(x)

	def printInfo(self):
		print( "======== model summary ========")
		print( "compartments: {}\nmembranes: {}".format(self.cStatus[0],self.cStatus[1]) )
		print( "compartment size:\n    {}\n   *{}\n   *{} m".format(self.cStatus[2],self.cStatus[3],self.cStatus[4]) )
		print( "time {}~{} s, output interval {} s ({} steps recorded)".format(self.timeStart,self.timeEnd,self.timeRecord,self.timeN) )
		print( "recorded symbols:" )
		for i in range(len(self.symbolOut)):
			print( "\t[{}]\t{}".format(i,self.symbolOut[i]) )

	def getSequence(self,s,x,y,z):
		""" timecourse of symbol [s] in compartment at [x][y][z].
			[s] must be a string.
			[x][y][z] must be integers.
			returns timecourse as a list of floats.
			upon error, raises error and aborts.
		"""
		# argument validation
		try:
			assert s in self.symbolOut, "error in getSequence(): could not find symbol \"{}\"".format(s)
			assert (x,y,z) in self.c, "error in getSequence(): no compartment at ({},{},{})".format(x,y,z)
		except AssertionError as e:
			raise

		result = []
		cid = self.c[(x,y,z)]
		index = self.symbolOut.index(s)
		for i in range(self.timeN):
			self.f.seek( self.offsetResults + i * (len(self.symbolOut)*self.cStatus[0]*8+4) )
			self.f.seek( 4,1 )
			self.f.seek( index*self.cStatus[0]*8, 1 )
			self.f.seek( cid*8, 1 )
			result.append( unpack("<d", self.f.read(8))[0] )
		return result


