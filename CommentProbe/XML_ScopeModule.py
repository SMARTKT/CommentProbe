"""
XML_ScopeModule.py obtains the Comments Placement feature (it is getting called in XML_GetExcelForAFile.py)
	XML_ScopeModule is used to get scope for the comments. It gives the start line number and end line number for the scope of the comment, i.e. the region for which the comment can be said to be applicable
[Command for running it individually] python2 XML_ScopeModule.py pngimage.c
[Input] Code file, comments.p
[Output] scope.p
"""
import sys
import re
import glob
import os
import pickle

# Returns data from comments.p file (comment, start and end line number of comment)
def getComments():
	comments = pickle.load( open( "comments.p", "rb" ) )
	return comments

# Given a C/C++ code removes all comments from it
def removeComments(content):
	index = 0
	comment_line_inside = False    # this is true when currently index is at a line comment (//)
	comment_block_level = 0  	   # this is non-zero when currently index is in a block comment (/* */)
	result = []					   # this contains the code without the comments
	while index < len(content):
		# on detecting /* change comment_block_level
		if content[index] == '/' and index + 1 < len(content) and content[index+1] == '*':
			comment_block_level += 1
		# on detecting */ change comment block level
		elif content[index] == '/' and content[index-1] == '*':
			comment_block_level -= 1
		# on detecting // set comment_line_inside to True
		elif content[index] == '/' and index + 1 < len(content) and content[index + 1] == '/':
			comment_line_inside = True
		# on detecting \n the line comment is over, so set comment_line_inside to False
		elif content[index] == '\n' and comment_line_inside == True:
			comment_line_inside = False
		# add letters to result if currently no comment is ongoing
		elif not comment_line_inside and comment_block_level == 0:
			result.append(content[index])
		index += 1

	return ''.join(result)

# This function takes a code (split into lines) and a start line number, and finds first unmatched }
def findClosingBrace(lines, start_line):
	count = 1
	while start_line < len(lines):
		now = removeComments(lines[start_line])
		for i in range(len(now)):
			if now[i] == '{':
				count += 1
			elif now[i] == '}':
				count -= 1
			if count == 0:
				return start_line
		start_line += 1
	return start_line

def min(x, y):
	if x < y:
		return x
	return y

def getScopeForAFile(file, results):
	# Read the code from the .c or .cpp file
	f = open(file, 'r')
	text = f.read()
	lines = text.split("\n")
	f.close()
	
	# Reading the comments extracted from the file	
	comments = getComments()

	scope = [0] * len(comments)
	i = 0
	while i < len(comments):
		# Current Comment, start line, end line. (Basically a useless comment :P)
		comment = comments[i]
		start_line = int(comment[1]) - 1
		end_line = int(comment[2]) - 1

		# Rule 1: (Inline comments) If the starting line of the comment has any other code?
		"""
		Example : /*this variables stores the count*/ counter = 1;
		"""
		code = removeComments(lines[start_line])
		code.replace('\t', ' ')
		content = code.strip(" ")
		if len(content) > 0 and content[-1] != '{':      # There by excluding the open brace case. 
			scope[i] = (start_line + 1, end_line + 1)
			i += 1
			print i, "rule 1"
			continue

		# Find the next line in the code.
		"""
		Example : 
		/* the function checks 
		whether the number is 
		prime or not
		*/


		bool is_prime();    <--- Then nxline index is brought to this line    
		"""
		nxline = end_line + 1
		while nxline < len(lines):
			line_now = lines[nxline].replace(" ", "")
			if line_now != "":
				break
			nxline += 1

		# if the end of file is reached, scope of comment has no code lines
		if nxline == len(lines):
			scope[i] = (nxline, len(lines))
			i += 1
			continue

		end_line = nxline - 1
		# Treating multiple consecutive comments as the same comment
		# Handles the case of inline comments and blank lines.
		# comments with indices from i to j-1 will have the same scope.
		"""
		For example : 
		/* comment 1 */

		/* comment 2 */

		/* comment 3 */
		"""
		j = i+1
		while j < len(comments) and comments[j][1] - 1 == end_line + 1:
			# If inline comment, then don't include it
			code = removeComments(lines[end_line + 1])
			code.replace('\t', ' ')
			content = code.strip(" ")
			if len(content) > 0:
				break

			# Else update the end_line
			end_line = comments[j][2] - 1
			# Remove the blank lines
			while end_line + 1 < len(lines):
				line_now = lines[end_line + 1].replace(" ", "")
				if line_now != "":
					break
				end_line += 1
			j += 1	

		# Rule 2: Comment follows #include. (Global comment or Header comment)
		code = removeComments(lines[nxline])
		code.replace('\t', ' ')
		content = code.strip(" ")
		if content.startswith("#include"):
			print i, "rule 2"
			for ind in range(i, j):
				scope[ind] = (start_line + 1, len(lines))
			i = j
			continue

		# Rule 3: (Block following it) Comment having start brace before or after it.
		# The very next line is ending with a closed brace
		if len(content) > 0 and content[-1] == '{':
			print i, "rule 3, case 1"
			for ind in range(i, j):
				scope[ind] = (start_line + 1, findClosingBrace(lines, nxline + 1) + 1)
			i = j
			continue

		# Find the next to next line in the code.
		nxnxline = nxline + 1
		while nxnxline < len(lines):
			line_now = lines[nxnxline].replace(" ", "")
			if line_now != "":
				break
			nxnxline += 1

		if nxnxline < len(lines):
			code = removeComments(lines[nxnxline])
			code.replace('\t', ' ')
			content = code.strip(" ")

			if len(content) > 0 and content[0] == '{':
				print i, "rule 3 part2"
				for ind in range(i, j):
					scope[ind] = (start_line + 1, findClosingBrace(lines, nxnxline + 1) + 1)
				i = j
				continue

		# Rule 4: Find next comment
		print i, "rule 4"
		block_end = findClosingBrace(lines, nxline) + 1
		if j < len(comments):
			for ind in range(i, j):
				scope[ind] = (start_line + 1, min(block_end, int(comments[j][1]) - 1))
		else:
			for ind in range(i, j):
				scope[ind] = (start_line + 1, block_end)
		i = j
	return scope

# First the data from comments.p (generated by XML_CommentExtractor.py and contains comments, their start and end line numbers) is read
# Then getScopeForAFile() generates scope data which gets stored in scope.p
# It gives the start line number and end line number for the scope of the comment, i.e. the region for which the comment can be said to be applicable
if len(sys.argv) != 2:
	print("Give one argument as filename")
	exit(-1)
results = getComments()
scopes = getScopeForAFile(sys.argv[1], results)

with open("scope.p", 'wb') as fp:
	pickle.dump(scopes, fp, protocol=2)

print scopes
