#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  StanfordParsing.py for comment analysis of c/c++ programs using AST and POS and dependencies
#
#  Copyright 2018 Shakti <shakti@shakti-Inspiron-5559>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


"""
classify_batched takes the knowledge base and adds the following columns to it => "Comment sentences", "Operational/Descriptional", "Is Conditional", "Rule triggered", "POS Tags"
The function classifyComments in classify_batched makes the data for these 5 columns. classifyComments uses findDependencies_batched(which uses Stanford Dependency Parser) and classifySentence classifies sentences into description or operation classes based on predefined rules.
[Command for running it individually] python2 classify_batched.py ../knowledge_base.csv
[Input] knowledge_base.csv
[Output] knowledge_base.csv
"""


import os
import re
import nltk
import sys
nltk.data.path.append('/home/dewang/nltk_data')
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag, word_tokenize, sent_tokenize

from nltk.parse.stanford import StanfordParser
from nltk.tree import ParentedTree, Tree
from nltk import tokenize
import graphviz
from nltk.parse.stanford import StanfordDependencyParser
import pickle

from nltk import pos_tag

import re
import csv

def sentence_splitter(sentence) :
	re.findall(r"[\w']+|[.,!?;]", sentence)

#def words_tok(text) :
#	return re.findall("[\O\Θ\Ωa-zA-Z0-9'!#$%&*+-_/=?`{|}~.\"\(\):;.,]+", text, re.UNICODE)

informativeCommentCheckList = ['copyright','warranty','merchantability','public license', 'program for', 'application for' , 'code for', 'prg for' , 'C code', 'C program']


path_to_jar = '../StanFordParser/stanford-parser-full-2015-12-09/stanford-parser.jar'
path_to_models_jar = '../StanFordParser/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar'

os.environ['STANFORD_PARSER'] = path_to_jar
os.environ['STANFORD_MODELS'] = path_to_models_jar
Words = dict()

def find_subject(t):
  for s in t.subtrees(lambda t: t.label() == 'NP'):
    for n in s.subtrees(lambda n: n.label().startswith('NN')):
      return (n[0], find_attrs(n))



def find_predicate(t):
  v = None

  for s in t.subtrees(lambda t: t.label() == 'VP'):
    for n in s.subtrees(lambda n: n.label().startswith('VB')):
      v = n
  return (v[0], find_attrs(v))


def find_object(t):
  for s in t.subtrees(lambda t: t.label() == 'VP'):
    for n in s.subtrees(lambda n: n.label() in ['NP', 'PP', 'ADJP']):
      if n.label() in ['NP', 'PP']:
        for c in n.subtrees(lambda c: c.label().startswith('NN')):
          return (c[0], find_attrs(c))
      else:
        for c in n.subtrees(lambda c: c.label().startswith('JJ')):
          return (c[0], find_attrs(c))



def find_attrs(node):
  attrs = []
  p = node.parent()

  # Search siblings of adjective for adverbs
  if node.label().startswith('JJ'):
    for s in p:
      if s.label() == 'RB':
        attrs.append(s[0])

  elif node.label().startswith('NN'):
    for s in p:
      if s.label() in ['DT','PRP$','POS','JJ','CD','ADJP','QP','NP']:
        attrs.append(s[0])

  # Search siblings of verbs for adverb phrase
  elif node.label().startswith('VB'):
    for s in p:
      if s.label() == 'ADVP':
        attrs.append(' '.join(s.flatten()))

  # Search uncles
  # if the node is noun or adjective search for prepositional phrase
  if node.label().startswith('JJ') or node.label().startswith('NN'):
      for s in p.parent():
        if s != p and s.label() == 'PP':
          attrs.append(' '.join(s.flatten()))

  elif node.label().startswith('VB'):
    for s in p.parent():
      if s != p and s.label().startswith('VB'):
        attrs.append(' '.join(s.flatten()))

  return attrs




def check(sent) :

	parser = StanfordParser()

	# Parse the example sentence


	# print(sent)
	t = list(parser.raw_parse(sent))[0]
	# print(t)
	t = ParentedTree.convert(t)
	# print(t)
	# t.pretty_print()
	try :
		subj = find_subject(t)
	except :
		subj = []
	try :
		pred = find_predicate(t)
	except :
		pred = []
	try :
		obj =  find_object(t)
	except :
		obj = []

	# print (subj)
	# print (pred)
	# print (obj)
	return subj , pred , obj

def findDependencies(parsetree) :
	global Words
	Words = dict()

	root_tag = []
	roots = []
	pos_tagging = []

	dependencyList= []
	maxIndex = -1
	try :
		for k in parsetree.nodes.values():
			if k["ctag"] != None and k["word"] != None:
				w = k['word']
				address = int(k['address']) - 1
				pos_tagging.append([address,w,k['ctag']])
				Words[address] = w
				if maxIndex < address :
					maxIndex = address
	except :
		# print("Error in creating pos tagging")
		# exit(-1)
		pos_tagging = []
		return pos_tagging , roots , dependencyList , Words

	for i in range(0, maxIndex + 1) :
		try :
			x = Words[i]
		except :
			Words[i] = ""
	# print("-------------- Dictionary Of Words ----------------------------")
	# print(Words)

	try:
		for k in parsetree.nodes.values():

			if k["head"] == 0:
				root_tag.append(str(k["rel"])  + "(" + "Root" + "-" + str(k["head"]) + "," + str(k["word"]) + "-" + str(k["address"]) + ")" )
				rootAddress = k["address"] - 1
				leftWords = []
				rightWords = []
				for i in range(0, rootAddress) :
					leftWords.append(Words[i])
				for i in range(rootAddress + 1 , maxIndex + 1) :
					rightWords.append(Words[i])



				roots.append([rootAddress,k["word"], leftWords , rightWords])
				# print(k)
			else:
				pass
				# print(k)
			if k["ctag"] != None and k["word"] != None:
				w = k['word']
				address = int(k['address']) - 1
				t1 = (w , address)
				#print("***** Deps for word " + w)
				cdepts = k['deps']
				# print("****************Test1******************")
				# print(cdepts)
				for key in cdepts :
					# print("Key = ")
					#print(key)
					dependencies = cdepts[key]
					# print("******************Test2***************")
					for dep in dependencies :
						# print("Dep  =")
						#print(dep)

						# print("Words at dep = ")
						# print(Words[int(dep)-1])
						addr = int(dep) - 1
						t2 =(Words[addr] , addr )
						dependencyList.append([key , t1 , t2])
					# print("*****************************************")

	except :
		print("Error in reading nodes of the tree")
		# exit(-1)
	# print(root_tag)
	# print(roots)
	# print("POS-Tagging")
	# print(pos_tagging)
	'''
	dependencyList = []
	try :
		res = dependency_parser.raw_parse(sentence)
		dep = res.__next__()
		depList = list(dep.triples())

		for x in depList :
			print(x[0])
			print(x[1])
			print(x[2])
			print('------------------')
			dependencyList.append([x[0],x[1],x[2]])
	except :
		print("Error in finding dependencies")

	print("____________________________________________________________________")
	'''
	# print(dependencyList)
	i = 0
	while i < len(Words) :
		try :
			x = Words[i]
		except :
			Words[i] = ""
		i = i + 1



	return pos_tagging , roots , dependencyList, Words

def findDependencies_batched(sentences):
    #try :
	dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
	results = dependency_parser.raw_parse_sents(sentences)
	results = list(results)
	if(len(results) != len(sentences)):
		print("#######WARNINING: Len(results) != Len(sentences) - ",len(results), len(sentences))
    #except :
	#       print("Error in parsing the tree")
		# exit(-1)

	all_pos_tagging = []
	all_roots = []
	all_dependencyList = []
	all_Words = []

	for parsetree in results:
	    pos_tagging, roots, dependencyList, Words = findDependencies(list(parsetree)[0])
	    all_pos_tagging.append(pos_tagging)
	    all_roots.append(roots)
	    all_dependencyList.append(dependencyList)
	    all_Words.append(Words)

	if len(all_pos_tagging) != len(sentences):
	    print("#####WARNINING: Len(all_pos_tagging) < Len(sentences) - ",len(all_pos_tagging), len(sentences))

	while(len(all_pos_tagging) < len(sentences)):
	    all_pos_tagging.append([])
	    all_roots.append([])
	    all_dependencyList.append([])
	    all_Words.append([])

	return all_pos_tagging, all_roots, all_dependencyList, all_Words


def isOperation(word):
	word = word.lower()
	f = open("program_domain.csv", 'r')
	r = csv.reader(f)
	for each in r:
		if each[1].find("Operations") != -1 and each[0].lower() == word:
			return 1
	return 0

conditional_words = ["if", "as", "because", "before", "only", "whether", "unless", "until", "since", "provided", "providing", "whenever", "wherever"]
def isConditional(pos_tagging, words):
	for i in range(len(pos_tagging)):
		word_now = words[i].lower()
		if pos_tagging[i][2] == "IN" and word_now in conditional_words:
			return 1
	return 0

# Given a sentence classifies the sentence into
# description or operation classes.
# Returns four fields
# First field: operational/ description
#	  0 - description
#         1 - operation
# Second field: if conditional sentence - 1 else 0
# Third field: Rule which triggers operational/Conditional
# Fourth field: Operation if operational
def classifySentence(pos_tagging, roots, dependencyList, Words):
	# pos_tagging, roots, dependencyList, Words = findDependencies(sentence)
	is_condition = isConditional(pos_tagging, Words)
	if len(roots) == 0 or len(roots[0]) == 0:
		return [-1, -1, -1, ""]
	root_index = roots[0][0]
	if len(pos_tagging) <= root_index:
		return [-1, -1, -1, ""]
	root_pos = pos_tagging[root_index][2]
	root_word = Words[root_index]
	if root_pos.startswith("VB"):
		# If Root word present in the Vocab Dictionary as an operation
		if(isOperation(root_word)):
			# print "Operation found in Vocab Dictionary"
			return [1, is_condition, 1, root_word]
		elif root_pos in ["VBD", "VBN"]:
			# print "Pos tag found in description verb class"
			return [0, is_condition, 2, ""]
		else:
			# print "Pos tag not found in description verb class"
			return [1, is_condition, 3, root_word]
	else:
		# print "Root is not a verb"
		return [0, is_condition, 4, ""]

def classifySentence_batched(sentences):
    all_pos_tagging, all_roots, all_dependencyList, all_Words = findDependencies_batched(sentences)
    all_outs = []
    for i in range(len(sentences)):
        all_outs.append(classifySentence(all_pos_tagging[i], all_roots[i], all_dependencyList[i], all_Words[i]))

    return all_outs, all_pos_tagging

"""
Function used for processing of comment to build data used in feature - "descriptive", "operational / conditional", "non DT IN words"

"""
def classifyComment(comment):
	if comment == "":
		return [], ""
	comments = re.split(';|\n', comment)
	ans = ["", "", "", ""]
	trans = {0 : "d", 1 : "o", -1 : "e"}
	cond = {0 : "False", 1 : "True", -1: "Error"}
        ans_pos = ""
        all_outs, all_pos = classifySentence_batched(comments)
        for i, each in enumerate(comments):
		ans[0] += each + " | "
		out = all_outs[i]
		print "out: ", out, "trans: ", trans
		out[0] = trans[out[0]]
		if out[0] == "o":
			out[0] += ": " + out[3]
		out[1] = cond[out[1]]
		for i in range(3):
			ans[i+1] += str(out[i]) + " | "
	for i in range(4):
		ans[i] = ans[i][:-3]
        for each_pos in all_pos:
            for pos in each_pos:
            	#print("####POS -> ",str(pos[2]))
                ans_pos += str(pos[2]) + "|"
        ans_pos = ans_pos[:-1]
        return ans, ans_pos

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f)
	out = []
	for each in r:
		out.append(each)
	f.close()
	return out

def writeCSV(fname, arr):
	with open(fname, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
		for each in arr:
			spamwriter.writerow(each)

def classifyCSV(fname):
	knowledge_base = readCSV(fname)
	knowledge_base[0].extend(["Comment sentences", "Operational/Descriptional", "Is Conditional", "Rule triggered", "POS Tags"])

	# information for the features "descriptive", "operational / conditional", "non DT IN words" added to knowledge_base.csv
	for i in range(1,len(knowledge_base)):
		comment_text = knowledge_base[i][2]
		class_now, pos_tags_now = classifyComment(comment_text)
		#print("POS NOW -> ",pos_tags_now)
		knowledge_base[i].extend(class_now)
                knowledge_base[i].append(pos_tags_now)
                #print("##KB -> ",i,knowledge_base[i])
	writeCSV(fname, knowledge_base)

if len(sys.argv) != 2:
	print "Give one argument: filename of the knowledge base"
	exit(-1)
fname = sys.argv[1]
classifyCSV(fname)
