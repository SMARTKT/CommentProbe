"""
XML_FinalExcelGeneration uses the comments.p, scope.p and identifiers.csv generated from previous three codes to get : 
"File name" => name of the file
"Comment Id" => Ids, unique integers (like row number)
"Comment Text" => the actual comments (extracted by regex in XML_CommentExtractor)
"Comment Tokens" => after removing stopwords and symbols from the comment, splitting by spaces is done to get tokens
"Comment scope" => Was obtained in XML_ScopeModule.py
"Prog.dom matches (comm.)" and "Prob.dom matches (comm.)" => The tokens, two consecutive joined tokens, and three consecutive joined tokens are checked in problem domain and program domain to get these features
"Identifier symbol", "Identifier type", "Identifier tokens", "Identifier scopes", "prog.dom matches (id)", "prob. dom matches (id)" => For these features, first the overlap of scope of comments (from XML_ScopeModule) and overlap of each identifier (from xml_parsernew) is checked.
On match, the details of the identifier are included as feature.
"prog.dom matches (comm+id)", "prob. dom matches (comm+id)" => these are intersection of "prog.dom matches (id)"/"prob. dom matches (id)" with "Prog.dom matches (comm.)"/"Prob.dom matches (comm.)"
The output of XML_FinalExcelGeneration.py is saved in knowledge_base.csv
[Command for running it individually] python2 XML_FinalExcelGeneration.py pngimage.c Identifier/program_domain.csv libpng/ProblemDomainConcepts.txt
[Input] code file, vocab file, program domain file
[Output] knowledge_base.csv
"""
import sys
import re
import glob
import os
import csv

import pickle

def getIdentifierInfo():
	identifier_info = []
	f = open("Identifier/identifiers.csv", 'r')
	r = csv.reader(f)
	for each in r:
		identifier_info.append(each)
	f.close()
	return identifier_info

def getComments():
	comments = pickle.load( open( "comments.p", "rb" ) )
	return comments

def getProgramDomainWords(fname):
	f = open(fname, 'r')
	prog_dom_reader = csv.reader(f)
	dom_list = {}
	for row in prog_dom_reader:
		word = row[0].lower()
		if word != "":
			dom_list[word] = row[1]
	f.close()
	return dom_list

def getProblemDomainWords(fname):
	f = open(fname, 'r')
	text = f.read()
	text = text.split("\n")
	dom_list = {}
	for row in text:
		if row != "":
			dom_list[row.strip().lower()] = "ProblemDomain"
	f.close()
	return dom_list

def getScope():
	with open("scope.p", 'r') as fp:
		scopes = pickle.load(fp)
	return scopes

IDENTIFER_INFO = getIdentifierInfo()
COMMENTS = getComments()   # The comments data which is read from comments.p
PROGRAM_DOMAIN_WORDS = getProgramDomainWords(sys.argv[2])  # The words list read from program domain file and used for feature - "application specific entities count"
PROBLEM_DOMIAN_WORDS = getProblemDomainWords(sys.argv[3])  # The words list read from problem domain file and used for feature - "software development count"
SCOPES = getScope()

# Returns comments from the database


"""
list of the stopwords for comment cleanup
Used for feature - "count of comment tokens"
"""
stop_words = ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'after', 'few', 'whom', 't', 'being', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than']

"""
Function that returns the given string without the stopwords
Used for features - "count of comment tokens"
"""
def removeStopWords(s):
	s.replace('\n', ' ')
	s.replace('\t', ' ')
	s = s.split(" ")
	ans = ""
	for each in s:
		now = each.lower()
		if now in stop_words or now == "":
			continue
		ans += now + " "
	return ans

"""
Filtering of comment
Used for feature - "count of comment tokens"
"""
def getFilteredComment(comment):
	l = ["?", '"', ".", "#", "!", "$", "%", "&", "^", "*", "(", ")", "~", "`", "+", "/", ",", "|", ":", ";", "\n", "\\", "@", "$", "=", ">", "<"]
	for each in l:
		comment = comment.replace(each, " ")
	comment = comment.replace("'", "")
	comment = removeStopWords(comment)
	return comment

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
Function to get intermediate data for features - "count of comment tokens", "software development count" , "application specific entities count", "coherence inconsistent", "coherence redundant"
"""
def getConceptMatches(comment_text, vocab_loc, probdom_loc):
	#vocab_map = getProgramDomainWords(vocab_loc)
	#probdom_map = getProblemDomainWords(probdom_loc)
	filetered_comment = getFilteredComment(comment_text)
	tokens = filetered_comment.split(" ")
	grams = getGrams(filetered_comment)
	vocab_matches = []
	prob_matches = []
	for tok in grams:
		if tok in PROGRAM_DOMAIN_WORDS:
			vocab_matches.append([tok, PROGRAM_DOMAIN_WORDS[tok]])
		if tok in PROBLEM_DOMIAN_WORDS:
			prob_matches.append(tok)
	return (vocab_matches, prob_matches, tokens)


# def getCommentIdentifierMatches():

"""
Used for feature - "coherence inconsistent", "coherence redundant", "scope score"
"""
def isScopeMatch(sa, sb):
	if sa[0] <= sb[0] and sa[1] >= sb[1]:
		return True
	if sa[0] <= sb[1] and sa[1] >= sb[1]: 
		return True
	return False

from difflib import SequenceMatcher

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio() >= 0.9

"""
Function that joins a given list elements by given delimiter
Used for feature - "count of comment tokens"
"""
def joinByDel(l, d):
	output = ""
	if len(l) == 0:
		return ""
	for i in range(len(l) - 1):
		output += str(l[i]) + d + " "
	output += str(l[-1])
	return output



def constructGraph(fname, vocab_loc, probdom_loc):
	"""
	identifier_info is copied from IDENTIFER_INFO which is used to determine id_matches_prog and id_matches_prob
	Used to determine feature - "coherence inconsistent", "coherence redundant", "scope score"
	"""
	identifier_info = IDENTIFER_INFO

	#comments = getComments()
	#scopes = getScope()
	output = [["File name", "Comment Id", "Comment Text", "Comment Tokens", "Comment scope", "Prog.dom matches (comm.)", "Prob.dom matches (comm.)", "Identifier symbol", "Identifier type", "Identifier tokens", "Identifier scopes", "prog.dom matches (id)", "prob. dom matches (id)", "prog.dom matches (comm+id)", "prob. dom matches (comm+id)"]]

	for i in range(len(COMMENTS)):
		comment_text = COMMENTS[i][0]  # the comment. On this getConceptMatches is called to get intermediate data for feature - "count of comment tokens", "software development count", "application specific entities count"
		scope_now = SCOPES[i] 	# indicates the current scope (ith element of scopes.p) Used for feature - "coherence inconsistent", "coherence redundant", "scope score"

		print "+++ Comment now:", comment_text
		"""
		tokens variable is used for feature - "count of comment tokens"
		vocab_matches variable is used for feature - "software development count", "coherence inconsistent"
		prob_matches variable is used for feature - "application specific entities count"
		"""
		(vocab_matches, prob_matches, tokens) = getConceptMatches(comment_text, vocab_loc, probdom_loc)
		print "Vocab matches:", vocab_matches
		print "Prob matches:", prob_matches

		"""
		id_matches_prog is used for feature : "coherence inconsistent"
		id_matches_prob is used for feature : "coherence redundant"

		id_matches_type and id_matches_scope are used for the feature : "scope score"
		"""
		id_matches_symbol = []
		id_matches_tokens = []
		id_matches_type = []
		id_matches_scope = []
		id_matches_prog = []
		id_matches_prob = []
		skip_header = False
		for each in identifier_info:
			if each[0] == "":
				continue
			if skip_header == False:
				skip_header = True
				continue
			if isScopeMatch(scope_now, [int(each[2]), int(each[3])]):
				id_matches_symbol.append(each[0])
				id_matches_tokens.append(each[5])
				id_matches_type.append(each[1] + " : " + each[4])
				id_matches_scope.append(joinByDel(each[2:4], ":"))
				id_matches_prog.append(each[6])
				id_matches_prob.append(each[7])

		"""
		id_comment_prog_matches is used for the feature - "coherence inconsistent"
		id_comment_prog_matches uses vocab_matches and id_matches_prog
		vocab_matches is obtained using getConceptMatches()

		id_comment_prob_matches is used for the feature - "coherence redundant"
		id_comment_prob_matches uses vocab_matches and id_matches_prob
		vocab_matches is obtained using getConceptMatches()
		"""
		id_comment_prog_matches = []
		id_comment_prob_matches = []
		for each in id_matches_prog:
			domain_word_now = each.split(" : ")[0]
			for every in vocab_matches:
				if every[0] == domain_word_now and every[0] != "":
					id_comment_prog_matches.append(every[0])
		for each in id_matches_prob:
			for every in prob_matches:
				if every == each and every != "":
					id_comment_prob_matches.append(every[0])

		"""
		Data row added to be put in knowledge_base.csv
		joinByDel(tokens, " |||") is for the feature - "count of comment tokens"
		joinByDel(vocab_matches, " ") is for the feature - "software development count"
		joinByDel(prob_matches, " |||") is for the feature - "application specific entities count"
		joinByDel(id_comment_prog_matches, " |||") is for the feature - "coherence inconsistent"
		joinByDel(id_comment_prob_matches, " |||") is for the feature - "coherence redundant"
		joinByDel(scope_now, ":"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_scope, " |||") are for the feature - scope_score
		
		"""
		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
	if len(output) > 1:
		outfile = open("knowledge_base.csv", 'wb')
		writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
		for eachrow in output:
			writer.writerow(eachrow)
		outfile.close()

if len(sys.argv) != 4:
	print("Give 3 arguments: filename, vocab dictionary location, problem domain location in order")
	exit(-1)

constructGraph(sys.argv[1], sys.argv[2], sys.argv[3])
