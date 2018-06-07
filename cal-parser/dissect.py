#!/usr/bin/env python3

# parser? for .cal files produced by A-cell simulations
# works, but messy. magic numbers everywhere.

import struct
import sys

# timecourse of [s]th symbol in [c]th compartment.
#     intended usage:
#         print( getSequence(fin,11,cp[x,y,z]) )
def getSequence(fin,s,c):
	try:
		assert s<n_out, "error in getSequence(fin,s,c): expected s < n_out"
		assert c<cmp_stat[0], "error in getSequence(fin,s,c): expected c < cmp_stat[0]"
	except AssertionError as e:
		print(e)
		return
	seq = []
	for i in range(time_points):
		fin.seek( result + i* (n_out*cmp_stat[0]*8+4) )
		fin.seek( 4,1 )
		fin.seek( s*cmp_stat[0]*8, 1 )
		fin.seek( c*8, 1 )
		seq.append(struct.unpack( "<d", fin.read(8) )[0])
		#seq.append( "0x{:x}".format(fin.tell()) )
	return seq

time_start = 0.0
time_end   = 0.0
time_calc  = 0.0
time_out   = 0.0
time_points = 0
symbol = []
symbol_unit = []
n_out = 0
symbol_out = []
result = 0	# byte offset of results
cp = {}	# compartment{(x,y,z)} = id
with open("out.cal","rb") as fin:
	# header
	fin.seek(160)

	# *Information****
	fin.seek(16,1)
	size = int.from_bytes(fin.read(4), byteorder="little")
	fin.seek(size,1)

	# *VsimFile*******
	fin.seek(16,1)
	#size = int.from_bytes(fin.read(4), byteorder="little")
	#print( size )
	#fin.seek(size,1)
	fin.seek(4+512,1)

	# *Symbol List****
	fin.seek(16,1)
	n_symbol = int.from_bytes(fin.read(4), byteorder="little")
	for i in range(n_symbol):
		size = int.from_bytes(fin.read(4), byteorder="little")
		symbol.append( fin.read(size).decode() )
		size = int.from_bytes(fin.read(4), byteorder="little")
		symbol_unit.append( fin.read(size).decode() )
		fin.seek(4*5 + 8*7,1)
		#print("\t"+ symbol[i] +" ["+ symbol_unit[i] +"]")

	# *CalcCondition**
	fin.seek(16,1)
	(time_start, time_end, time_calc, time_out) = struct.unpack("<dddd",fin.read(32))	# start, end, calculation interval, output interval
	time_points = int( (time_end-time_start) / time_out +1 )

	# *OutputSymbols**
	fin.seek(16,1)
	n_out = int.from_bytes(fin.read(4), byteorder="little")
	for i in range(n_out):
		size = int.from_bytes(fin.read(4), byteorder="little")
		symbol_out.append(  fin.read(size).decode() )

	# *Stimulation****
	fin.seek(16,1)
	x = int.from_bytes(fin.read(4), byteorder="little")
	for i in range(x):
		pass

	# *CompartmentSt.*
	fin.seek(16,1)
	cmp_stat = struct.unpack("<iiddd",fin.read(8+24))
	#fin.seek(21*cmp_stat[0],1)
	for i in range(cmp_stat[0]):
		cp[ struct.unpack("<iiiBii",fin.read(21))[0:3] ] = i	# not sure if this is a proper solution

	# *SymbolValues***
	# initial values
	# TODO: should ba able to handle cases with N_TRANS, N_EXTRA, N_INTRA, etc.
	fin.seek(16,1)
	fin.seek(8*cmp_stat[0]*n_symbol,1)
	#for j in range(n_symbol):
	#	for i in range(cmp_stat[0]):
	#		x = struct.unpack("<d",fin.read(8))

	# *results********
	fin.seek(16,1)

	result = fin.tell()
	#for j in range(time_points):
	#	fin.seek(4,1)	# "transform"; always zero?
	#	for i in range(cmp_stat[0]):
	#		x = struct.unpack("<d",fin.read(8))



	#----------------
	# the fun part.
	#----------------



	# check file size
	fin.seek(0,2)
	size_estimate = 8*cmp_stat[0]*n_out*(time_points) + 4*(time_points)
	size_records = fin.tell() - result
	if( size_estimate > size_records ):
		x = size_records / (8*cmp_stat[0]*n_out + 4)
		x = x-1		# because the first step is only the initial parameters
		if(len(sys.argv)==1):
			print("actual file size is smaller than expected, found only {} steps (= {:.3f} s)".format(x, x*time_out))
		time_points = int(x)

	# when no options are supplied, print summary and exit
	if(len(sys.argv)==1):
		print( "model summary:\n\tcompartments: {}\n\tmembranes: {}\n\tcompartment size: {} * {} * {}m".format(cmp_stat[0], cmp_stat[1], cmp_stat[2], cmp_stat[3], cmp_stat[4]) )
		#print( "\tcoordinates: {}".format(cp))
		print( "time {}~{} s, output interval {} s (= {} steps)".format(time_start, time_end, time_out, time_points) )
		print( "recorded symbols:" )
		for i in range(len(symbol_out)):
			print( "\t[{}]\t{}".format(i, symbol_out[i]) )
		sys.exit()

	time_points = time_points +1

	output = []
	target = 13
	scan = []

	# scan the bottom-most layer in model
	z = -103
	for x in range(-38,38+1):
		for y in range(-38,38+1):
			if(x,y,z) in cp:
				scan.append( getSequence(fin,target,cp[x,y,z]) )
	output.append( [sum(x)/len(scan) for x in zip(*scan)] )

	# scan the interdiscal cytosol between adjacent discs
	for layers in [ [bleh,bleh+1] for bleh in range(-99,102,5) ]:
		scan = []
		for z in layers:
			for x in range(-38,38+1):
				for y in range(-38,38+1):
					if(x,y,z) in cp:
						scan.append( getSequence(fin,target,cp[x,y,z]) )
		output.append( [sum(x)/len(scan) for x in zip(*scan)] )

	# scan vertically
	#for z in range(-200,200+1):
	#	if(0,38,z) in cp:
	#		output.append( getSequence(fin,target,cp[0,38,z]) )

	# scan all compartments in model
	#for i in range(cmp_stat[0]):
	#	scan.append( getSequence(fin,target,i) )
	#output = [sum(x)/len(scan) for x in zip(*scan)]

	for column in range(len(output)):
		print( output[column] )
