#!/usr/bin/env python3

# sample script for calfile module

from calfile import CalFile

cf = CalFile("SAMPLE_CAL_FILE.cal",verbose=True)
cf.printInfo()
print( cf.getSequence("SYMBOL_NAME",0,0,1) )


