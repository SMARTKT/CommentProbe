"""
XML_CommentExtractor uses regular expressions to get comments, their start and end line number
	XML_CommentExtractor is used to get comments from the code file using regular expressions, and put the extracted data in comments.p
	Data put in comments.p consists of - start line number of each comment, end line number of each comment and the comment.
[Command for running it individually] python2 XML_CommentExtractor.py pngimage.c
[Input] Code file
[Output] comments.p
"""
import pickle
import sys
import re

"""
getComments is used to get comments, their start and end line number using regular expression from a given file name
"""
def getComments(filename):

	# Reading the contents of the file - "text" contains the complete contents, and "lines" is the text split into lines
	file = open(filename , "r")
	text = file.read()
	file.close()
	file = open(filename , "r")
	lines = file.readlines()
	file.close()

	# Extracting comments, their start and end line number using regular expressions
	all_comments = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE).findall(text)
	comment_iterator = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
	l = [(m.start(0), m.end(0)) for m in re.finditer(comment_iterator, text)]	

	start_line = []
	end_line = []
	for pos in range(0, len(all_comments)):
		location = l[pos][0]
		s = text[:location + 1]
		lineNo1 = s.count('\n') + 1
		location1 = l[pos][1]
		s = text[:location1 + 1]
		lineNo2 = s.count('\n')
		start_line.append(lineNo1)
		end_line.append(lineNo2)

		# the symbols for comments i.e. // or /* */ are removed along with trailing whitespace
		if all_comments[pos].startswith("//"):
			all_comments[pos] = all_comments[pos][2:]
		else:
			all_comments[pos] = all_comments[pos][2:-2]

		all_comments[pos] = all_comments[pos].strip()

	# result is a list of lists where each inner list is of size 3 and has - comment, its start line number and end line number
	result = []

	for pos in range(0, len(all_comments)):

		text = all_comments[pos]
		start = start_line[pos]
		end = end_line[pos]

		if end < start:
			end = start
			
		#bundling consecutive single line comments
		if len(result) > 0 and lines[start - 1].strip().startswith("//") and result[-1][2] == start - 1:
			result[-1][0] = result[-1][0] + "\n" + text
			result[-1][2] = start

		else:
			result.append([text, start, end])

	return result

def main():
	if len(sys.argv) != 2:
		print "Give one argument which is the location of the source code"
		exit(-1)
	fname = sys.argv[1]
	comments = getComments(fname)
	pickle.dump(comments, open( "comments.p", "wb" ) )

main()
