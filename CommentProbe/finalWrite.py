"""
finalWrite.py only rewrites the data of knowledge_base.csv to <codefilename with / replaced with underscore>_excel.csv. The data in the csv is exactly the same as knowledge base without any changes.
[Command for running it individually]python2 finalWrite.py pngimage.c knowledge_base.csv
[Input] knowledge_base.csv
[Output] <codefilename with / replaced with underscore>_excel.csv
"""
import csv
import os

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f)
	out = []
	for each in r:
		out.append(each)
	f.close()
	return out

def writeCSV(fname, csvloc):
	output = readCSV(csvloc)
	ofileloc = fname.replace("/", "_")
	print("Copyging: " + fname + " TO " + ofileloc)
	os.system("sudo cp " + fname + " " + "CSV/" + ofileloc) 
	outfile = open("CSV/" + ofileloc + "_excel.csv", 'wb')
	writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
	for eachrow in output: 
		writer.writerow(eachrow)
	outfile.close()

import sys
if len(sys.argv) != 3:
	print "Give two arguments which is C filename and csv location"
	exit(-1)

fname = sys.argv[1]
csvloc = sys.argv[2]
writeCSV(fname, csvloc)
