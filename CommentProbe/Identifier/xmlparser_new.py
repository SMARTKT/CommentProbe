"""
xmlparser_new parses the clang output xml file, uses functions findProgramDomainMatches and findProblemDomainMatches. These functions take a list of tokens.
	In xmlparser_new, the output consists of a list of lists where the inner list contains information : spelling, tag type, start an end line, matching program and problem domain words, type
	=> "Symbol", "Type", "Start line", "End line", "Data type", "Identifier tokens", "Program Domain matches", "Problem Domain matches"	
	This is saved into identifiers.csv
[Command for running it individually] python2 xmlparser_new.py ../pngimage_clang.xml ../pngimage.c  program_domain.csv ../libpng/ProblemDomainConcepts.txt
[Input] clang xml file, code file, vocab file, program domain file
[Output] identifiers.csv
"""
import xml.etree.ElementTree as ET 
import sys
import os
import csv
import sys

def getProgramDomainWords(fname):
	f = open(fname, 'r')
	prog_dom_reader = csv.reader(f)
	dom_list = {}
	for row in prog_dom_reader:
		word = row[0].lower()
		dom_list[word] = row[1]
	f.close()
	return dom_list

def getProblemDomainWords(fname):
	f = open(fname, 'r')
	text = f.read()
	text = text.split("\n")
	dom_list = {}
	for row in text:
		dom_list[row.lower()] = "ProblemDomain"
	f.close()
	return dom_list

def wordSegmentation(word):
	words = word.split("_")
	output = []
	for each in words:
		# Split if there is a change in lower to uppercase.
		# Eg: printArray is split as print, Array		
		i = 0
		j = 0
		while j < len(each):
			if j == len(each) - 1:
				output.append(each[i:j + 1])
				i = j + 1
			else:
				if each[j].islower() and each[j+1].isupper():
					output.append(each[i:j + 1])
					i = j + 1
			j += 1
	return output

def joinBySpace(l):
	if len(l) == 0:
		return ""
	ans = ""
	for each in l:
		if each != "":
			ans += each + " "
	return ans[:-1]

def getGrams(text):
	text = text.lower()
	words = text.split(" ")
	out = []
	for each in words:
		if each != "":
			out.append(each)
	
	words = out
	for i in range(0,len(words)-1):
		now = words[i] + " " + words[i+1]
		out.append(now)
	
	for i in range(0,len(words)-2):
		now = words[i] + " " + words[i+1] + " " + words[i+2]
		out.append(now)
	return out


"""
Function used for features - "coherence inconsistent"
"""
def findProgramDomainMatches(tokens):
	grams = getGrams(joinBySpace(tokens))
	vocab_dict = getProgramDomainWords(sys.argv[3])	
	output = ""
	for each in grams:
		now = each.lower()
		if now in vocab_dict:
			output += now + " : " + vocab_dict[now] + " | "
	return output[:-3]

"""
Function used for features - "coherence redundant"
"""
def findProblemDomainMatches(tokens):
	prob_dict = getProblemDomainWords(sys.argv[4])	
	output = ""
	for each in tokens:
		now = each.lower()
		if now in prob_dict:
			output += now + " | "
	return output[:-3]

def getAllTags(xmlfname):
	tree = ET.parse(xmlfname)
	elem_list = []
	for elem in tree.iter():
		elem_list.append(elem.tag)
	elem_list = list(set(elem_list))
	return elem_list

def parseXML(xmlfname, cfname, type_tag):
	# parsing of the xml tree
	tree = ET.parse(xmlfname)
	root = tree.getroot()
	data = []

	# start of main loop for building the data
	for each in root.findall(".//" + type_tag):
		dict_now = each.attrib	
		if "spelling" not in dict_now or dict_now["spelling"] is None or dict_now["spelling"] == 'None':
			continue
		try:
			location = dict_now["file"]
			if location == None:
				continue
			#print("L: ",location)
			#loc = location[:location.find('[')]
			loc = location
			print(loc)
			print(cfname)
			if os.path.basename(loc) == os.path.basename(cfname):
				print("HERE")
				symbol_now = dict_now["spelling"]
				type_now = dict_now["type"]
				#start_line = int(location[location.find('[') + 1 : location.find(']')])
				# start_line and end_line are defined using dict_now and and this information is used for the feature "scope score"
				start_line = int(dict_now['line'])
				end_line = dict_now["range.end"]
				end_line = int(end_line[1:-1].split(":")[0])
				#end_line = int(end_line[end_line.find('[') + 1 : end_line.find(']')])				
				tokens = wordSegmentation(symbol_now)
				prog_matches = findProgramDomainMatches(tokens)  # used for feature - "coherence inconsistent"
				prob_matches = findProblemDomainMatches(tokens)  # used for feature - "coherence redundant"
				data.append([symbol_now, type_tag, start_line, end_line, dict_now["type"], joinBySpace(tokens), prog_matches, prob_matches])
		except Exception as e:
			print("except:",e)
			print(dict_now)
			break
	return data

def main():
	if len(sys.argv) != 5:
		print "Give four arguments, the location of the xml file to be parsed, the location of the sourcecode, the location of the program domain words, the location of the problem domain words"
		exit(-1)

	xmlfname = sys.argv[1]
	cfname = sys.argv[2]
	print(xmlfname)
	tags = getAllTags(xmlfname)
	print("Out!")
	"""
	Getting the identifier related output
	Used for features - "coherence inconsistent", "coherence redundant", "scope score"
	"""
	output = []
	for tag in tags:
		print(tag)
		data = parseXML(xmlfname, cfname, tag) 
		output.extend(data)
	
	print "Identifier info:"
	print output
	f = open("identifiers.csv", 'w')
	writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(["Symbol", "Type", "Start line", "End line", "Data type", "Identifier tokens", "Program Domain matches", "Problem Domain matches"])
	for each in output:
		writer.writerow(each)
	f.close()

main()
