#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pynlpl.textprocessors import Classer
from pynlpl.statistics import FrequencyList
import sys

filename = sys.argv[1]

print >>sys.stderr, "Counting tokens"
f = open(filename)
freqlist = FrequencyList()
for i, line in enumerate(f):            
    if (i % 10000 == 0): 
        print >>sys.stderr, "\tLine " + str(i+1)
    line = ['<s>'] + line.strip().split(' ') + ['</s>']
    
    freqlist.append(line)
f.close()

print >>sys.stderr, "Building classer"
classer = Classer(freqlist, filesupport=True )
classer.save(filename + '.cls')

print >>sys.stderr, "Encoding data"
classer.encodefile(filename, filename + '.clsenc')
