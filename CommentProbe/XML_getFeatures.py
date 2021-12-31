"""
XML_getFeatures takes the _excel file and builds a file with the following columns : "#comment tokens", "#prog. conc", "#prob. conc", "descriptive", "operative", "conditional", "#scope_symbols", "#scope_functions", "scope_compound_statement1s", "scope_param", "scope_line_numbers", "prog_dom_match_identifiers", "prob_dom_match_identifiers", "copyright_license_comments", "libraries"
#comment tokens => Obtained from Comment Tokens columns by splitting the data in the column and counting number of tokens
#prog. conc => Obtained from Prog.dom matches (comm.) similar to #comment tokens, by splitting and counting number of tokens
#prob. conc => Obtained from Prob.dom matches (comm.) similar to #comment tokens, by splitting and counting number of tokens
descriptive => From Operational/Descriptional column of _excel file, based on count of descriptive and operational tokens, a score is calculated (which is weigted average weight 0.9 for description and 0.1 for operation)
operational => From Operational/Descriptional column of _excel file, based on count of descriptive and operational tokens, a score is calculated (which is weigted average weight 0.9 for operation and 0.1 for description)
conditional => Count of occurences of True in "Is Conditional" column
"#scope_symbols", "#scope_functions", "scope_compound_statement1s", "scope_param"	=> Using function getIdTypeInfo, Identifier type, Identifier scopes and Comment scope columns of _excel file are used. The identifier types are manually subdivided into three categories - func, var, statement. Based on starting scope of the identifiers and the comment scope, scores are calculated. #scope_symbols is sum of scores, while scope_functions, scope_compound_statements, scope_params are the individual scores
scope_line_numbers => The scope size (end-start+1) computed from Comment scope column of _excel file using getCommentLinesFunction
"prog_dom_match_identifiers" => Obtained from Prog.dom matches (comm.+id) similar to #comment tokens, by splitting and counting number of tokens
"prob_dom_match_identifiers" => Obtained from Prob.dom matches (comm.+id) similar to #comment tokens, by splitting and counting number of tokens
"copyright_license_comments" => This uses Comment Text column and determined in function getLibraryCopyrightInfo. If words "copyright" are present, this feature is 1 else 0
"libraries" => This uses Comment Text column and determined in function getLibraryCopyrightInfo. If words ".h" or "#include" are present, this feature is 1 else 0
This gets saved into <codefilename with / replaced with underscore>_feature.csv
[Command for running it individually]python2 XML_getFeatures.py pngimage.c_excel.csv
[Input] <codefilename with / replaced with underscore>_excel.csv
[Output] <codefilename with / replaced with underscore>_feature.csv
"""
import csv
import sys
import re

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f)
	out = []
	for each in r:
		while len(each) < 18:
			each.append("")
		out.append(each)
	f.close()
	return out

def writeCSV(fname, output):
	outfile = open(fname, 'wb')
	writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
	for eachrow in output: 
		writer.writerow(eachrow)
	outfile.close()

"""
getCount() returns the count of tokens and is used for features - "count of comment tokens", "software development count" ,"application specific entities count", "coherence inconsistent", "coherence redundant"
"""
def getCount(s, d):
	s = s.replace(" ", "")
	cnt = 0
	while s.find(d) != -1:
		cnt += 1
		s = s[s.find(d) + len(d) : ]
	return cnt

"""
Function used for features - "descriptive", "operational / conditional"
Function that takes the descriptional/operational column data of knowledge_base.csv and returns token count to be used in "descriptive" feature
"""
def numDescriptional(s):
	s = s.split("|")
	num = 0
	for each in s:
		now = each.replace(" ", "")
		if now == "":
			continue
		if now == "d":
			num += 1
	return num

"""
Function used for features - "descriptive", "operational / conditional"
Function that takes the descriptional/operational column data of knowledge_base.csv and returns token count to be used in "descriptive" feature
"""
def numOperational(s):
	s = s.split("|")
	num = 0
	for each in s:
		now = each.replace(" ", "")
		if now == "":
			continue
		now = now.split(":")
		if now[0] == "o":
			num += 1
	return num

def getIdClass(id_type):
	id_class = id_type.split(":")[0]
	return id_class.replace(" ", "")

import statistics
import math

def getIdscore(x, y, v):
	y = max(y, x)
	diff = float(y - x)
	diff = diff/float(v)	
	diff = diff * diff	
	return math.exp(-1*diff)

"""
Function used for feature "scope score"
"""
def getIdTypeInfo(s, l, comment_line):
	func = ["FUNCTION_DECL", "CALL_EXPR"]
	var = ["VAR_DECL", "PARM_DECL", "STRUCT_DECL", "DECL_REF_EXPR", "STRING_LITERAL", "FIELD_DECL", "TYPEDEF_DECL"]
	stmt = ["UNEXPOSED_EXPR", "MEMBER_REF_EXPR", "TYPE_REF"] 
	
	lines = []
	l = l.split(" |||")
	for i in range(len(l)):
		if l[i] != "":
			lines.append(float(l[i].split(":")[0]))

	if len(lines) >= 2:
		deviation = statistics.stdev(lines) + 0.1	
	else:
		deviation = 1.0

	s = s.split(" |||")
	ans = [0.1, 0.1, 0.1]
	for i in range(len(s)):
		each = s[i]		
		if each == "":
			continue
		
		id_class = getIdClass(each)
		if id_class in var:
			ans[2] += getIdscore(comment_line, lines[i], deviation)
		elif id_class in func:
			ans[0] += getIdscore(comment_line, lines[i], deviation)
		elif id_class in stmt:
			ans[1] += getIdscore(comment_line, lines[i], deviation)
		else:
			print "Not found for", each
	print "ans:", ans
	return ans

def getCommentLines(s):
	s = s.split(":")
	print s
	return int(s[1]) - int(s[0]) + 1

def getLibraryCopyrightInfo(text):
	ans = [0, 0]
	text = text.lower()
	if text.find("copyright") != -1:
		ans[0] = 1
	if text.find(".h") != -1 or text.find("#include") != -1:
		ans[1] = 1
	return ans

def getFeatures(fname):
	"""
	data read here is used for the feature - "count of comment tokens", "software development count", "application specific entities count" ,"non DT IN words", "coherence inconsistent", "coherence redundant", "scope score"
	"""
	data = readCSV(fname)
	features = [["#comment tokens", "#prog. conc", "#prob. conc", "descriptive", "operative", "conditional", "#scope_symbols", "#scope_functions", "scope_compound_statement1s", "scope_param", "scope_line_numbers", "prog_dom_match_identifiers", "prob_dom_match_identifiers", "copyright_license_comments", "libraries"]]
	for i in range(1, len(data)):
		line = data[i]
		feature = []
		feature.append(getCount(line[3], "|||"))    # For feature "count of comment tokens"
		feature.append(getCount(line[5], "]["))		# For feature "software development count"
		feature.append(getCount(line[6], "|||")) 	# For feature "application specific entities count"
		
		"""
		determining scores for the features - "descriptive", "operational / conditional"
		Weighted sum of num_desc and num_op
		"""
		num_desc = float(numDescriptional(line[16]))
		num_op = float(numOperational(line[16]))
		feature.append(num_desc * 0.9 + num_op * 0.1)
		feature.append(num_op * 0.9 + num_desc * 0.1)
		
		feature.append(len(re.findall("True", line[17]))) # For feature "non DT IN words"
		type_info = getIdTypeInfo(line[8], line[10], int(line[4].split(":")[0]))     # For feature "scope score" 		
		feature.append(type_info[0] + type_info[1] + type_info[2])		
		feature.extend(type_info) 				  # Information used for feature "scope score"
		feature.append(getCommentLines(line[4]))
		feature.append(getCount(line[13], "|||")) # For feature "coherence inconsistent"
		feature.append(getCount(line[14], "|||")) # For feature "coherence redundant"
		libcopyinfo = getLibraryCopyrightInfo(line[2])
		feature.extend(libcopyinfo)
		
		features.append(feature)
	
	ofname = fname.replace("excel", "feature")
	writeCSV(ofname, features)
	
	
if len(sys.argv) != 2:
	print "Give one argument which is the location of knowledge base csv"
	exit()

fname = sys.argv[1]
getFeatures(fname)
