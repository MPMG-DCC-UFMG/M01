#!/usr/bin/env python3
# -*- coding: utf-8

import sys
import numpy
import scipy.stats as stats


def average_and_ci(data, confidence_level = .95):
	avg = numpy.average(data)
	std = numpy.std(data, ddof=1)
	p = 1.0 - (1.0-confidence_level)/2
	confidence_interval = stats.t.ppf(p, len(data)-1)*std/(len(data)**0.5)
	return (avg, confidence_interval)


def read_float_values_from_file(file, field):
	v = []
	for line in file:
		if line != "" and line[0] != '*':
			try:
				spl = line.strip().split()
				if len(spl) < field:
					print ('Invalid field at line:', line, file=sys.stderr)
				else:
					v.append(float(spl[field - 1]))
			except:
				pass
	return v


#Programa principal


field = 1

if len(sys.argv) == 2:
    field = int(sys.argv[1])
values = read_float_values_from_file(sys.stdin, field)
(m, ci) = average_and_ci(values, 0.95)
print ("%.3f ± %.3f" % (m, ci))
#print ("%.3f" % m)




