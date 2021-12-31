"""
XML_CommentExtractor uses regular expressions to get comments, their start and end line number
	XML_CommentExtractor is used to get comments from the code file using regular expressions, and put the extracted data in comments.p
	Data put in comments.p consists of - start line number of each comment, end line number of each comment and the comment.
[Command for running it individually] python2 XML_CommentExtractor.py pngimage.c
[Input] Code file
[Output] comments.p

XML_ScopeModule.py obtains the Comments Placement feature (it is getting called in XML_GetExcelForAFile.py)
	XML_ScopeModule is used to get scope for the comments. It gives the start line number and end line number for the scope of the comment, i.e. the region for which the comment can be said to be applicable
[Command for running it individually] python2 XML_ScopeModule.py pngimage.c
[Input] Code file, comments.p
[Output] scope.p

xmlparser_new parses the clang output xml file, uses functions findProgramDomainMatches and findProblemDomainMatches. These functions take a list of tokens.
	In xmlparser_new, the output consists of a list of lists where the inner list contains information : spelling, tag type, start an end line, matching program and problem domain words, type
	=> "Symbol", "Type", "Start line", "End line", "Data type", "Identifier tokens", "Program Domain matches", "Problem Domain matches"	
	This is saved into identifiers.csv
[Command for running it individually] python2 xmlparser_new.py ../pngimage_clang.xml ../pngimage.c  program_domain.csv ../libpng/ProblemDomainConcepts.txt
[Input] clang xml file, code file, vocab file, program domain file
[Output] identifiers.csv

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

classify_batched takes the knowledge base and adds the following columns to it => "Comment sentences", "Operational/Descriptional", "Is Conditional", "Rule triggered", "POS Tags"
The function classifyComments in classify_batched makes the data for these 5 columns. classifyComments uses findDependencies_batched(which uses Stanford Dependency Parser) and classifySentence classifies sentences into description or operation classes based on predefined rules.
[Command for running it individually] python2 classify_batched.py ../knowledge_base.csv
[Input] knowledge_base.csv
[Output] knowledge_base.csv

finalWrite.py only rewrites the data of knowledge_base.csv to <codefilename with / replaced with underscore>_excel.csv. The data in the csv is exactly the same as knowledge base without any changes.
[Command for running it individually]python2 finalWrite.py pngimage.c knowledge_base.csv
[Input] knowledge_base.csv
[Output] <codefilename with / replaced with underscore>_excel.csv

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

XML_getFinalFeatures takes the excel_file, features file, xml file, code file as input
Using the comment text, it computes the following scores - bug_or_version_related, build_related, system_spec_related, build_details, authorship_related, email, date, author_details, copyright_or_license, junk
Using the <code filename>_feature.csv data, it computes the following scores - words, prog_conc, prob_conc, descriptional, conditional, operational, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score
Using the XML file and class NLP_features from NLP_features.py, the following are generated - description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports
These are saved into - <codefilename with / replaced with underscore>_train.csv
Columns in _train.csv are unnamed, the order is - filename, comment, words score, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score, build_details, author_details, junk, desription_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports 
[Command for running it individually] python2 XML_getFinalFeatures.py pngimage.c_excel.csv pngimage.c_features.csv pngimage_clang.xml pngimage.c
[Input] <codefilename with / replaced with underscore>_excel.csv, <codefilename with / replaced with underscore>_feature.csv, xml file, code file
[Output]<codefilename with / replaced with underscore>_train.csv


Mapping from columns in _train.csv to feature names : 
Header in _train.csv : Names
filename: Not applicable
comment: Not applicable
words: count of comment tokens
prog_conc: software development count
prob_conc: application specific entities count
descriptional: descriptive
operational: operational / conditional
conditional: non DT IN words
prog_domain_identifier_matches: coherence inconsistent
prob_domain_identifier_matches: coherence redundant
scope_score: scope score
build_details: application specific
author_details: developer details
junk: junk/copyright
desription_of_dataset: dataset description
working_summary: working summary
design_and_development: working summary - design
exception: allowed values, possible  exceptions
build_instr: build instructions
commits_and_bugs: project management
AST_symbols: construct names in comment
comment_placement: comment placements
usage_of_imports: libraries/imports



Description of columns for knowledge_base.csv
"File name" => name of the file
"Comment Id" => Ids, unique integers (like row number)
"Comment Text" => the actual comments (extracted by regex in XML_CommentExtractor getComments())
"Comment Tokens" => after removing stopwords and symbols from the comment, splitting by spaces is done to get tokens (XML_FinalExcelGeneration getConceptMatches())
"Comment scope" => Was obtained in XML_ScopeModule.py getScopeForAFile()
"Prog.dom matches (comm.)" and "Prob.dom matches (comm.)" => The tokens, two consecutive joined tokens, and three consecutive joined tokens are checked in problem domain and program domain to get these features (XML_FinalExcelGeneration getConceptMatches())
"Identifier symbol", "Identifier type", "Identifier tokens", "Identifier scopes", "prog.dom matches (id)", "prob. dom matches (id)" => For these features, first the overlap of scope of comments (from XML_ScopeModule.py getScopeForAFile()) and overlap of each identifier (from xmlparser_new) is checked(XML_FinalExcelGeneration isScopeMatch()).
On match, the details of the identifier are included as feature (XML_FinalExcelGeneration constructGraph()). 
"prog.dom matches (comm+id)", "prob. dom matches (comm+id)" => these are intersection of "prog.dom matches (id)"/"prob. dom matches (id)" with "Prog.dom matches (comm.)"/"Prob.dom matches (comm.) (XML_FinalExcelGeneration constructGraph())"
"Comment sentences" => The comment sentences joined by | ( FeatureDescOp/classify_batched.py classifyComment() )
"Operational/Descriptional" =>  Using function isOperational() and output of findDependencies_batched() in FeatureDescOp/classify_batched.py, classifySentence generates this feature(FeatureDescOp/classify_batched.py classifyComment())
"Is Conditional" => Uses functions isConditional() and output of findDependencies_batched() in FeatureDescOp/classify_batched.py these features are generated in FeatureDescOp/classify_batched.py classifyComment()
"Rule triggered", "POS Tags" => (FeatureDescOp/classify_batched.py classifyComment())



Description of columns for <code file>_features.csv
#comment tokens => Obtained from Comment Tokens columns by splitting the data in the column and counting number of tokens (XML_getFeatures getFeatures())
#prog. conc => Obtained from Prog.dom matches (comm.) similar to #comment tokens, by splitting and counting number of tokens (XML_getFeatures getFeatures())
#prob. conc => Obtained from Prob.dom matches (comm.) similar to #comment tokens, by splitting and counting number of tokens (XML_getFeatures getFeatures())
descriptive => From Operational/Descriptional column of _excel file, based on count of descriptive(XML_getFeatures numDescriptional()) and operational(XML_getFeatures numOperational()) tokens, a score is calculated (which is weigted average weight 0.9 for description and 0.1 for operation) (XML_getFeatures getFeatures())
operational => From Operational/Descriptional column of _excel file, based on count of descriptive(XML_getFeatures numDescriptional()) and operational(XML_getFeatures numOperational()) tokens, a score is calculated (which is weigted average weight 0.9 for operation and 0.1 for description) (XML_getFeatures getFeatures())
conditional => Count of occurences of True in "Is Conditional" column (XML_getFeatures getFeatures())
"#scope_symbols", "#scope_functions", "scope_compound_statement1s", "scope_param"	=> Using function getIdTypeInfo, Identifier type, Identifier scopes and Comment scope columns of _excel file are used. The identifier types are manually subdivided into three categories - func, var, statement. Based on starting scope of the identifiers and the comment scope, scores are calculated. #scope_symbols is sum of scores, while scope_functions, scope_compound_statements, scope_params are the individual scores (XML_getFeatures getFeatures())
scope_line_numbers => The scope size (end-start+1) computed from Comment scope column of _excel file using getCommentLinesFunction() (XML_getFeatures getFeatures())
"prog_dom_match_identifiers" => Obtained from Prog.dom matches (comm.+id) similar to #comment tokens, by splitting and counting number of tokens (XML_getFeatures getFeatures())
"prob_dom_match_identifiers" => Obtained from Prob.dom matches (comm.+id) similar to #comment tokens, by splitting and counting number of tokens (XML_getFeatures getFeatures())
"copyright_license_comments" => This uses Comment Text column and determined in function getLibraryCopyrightInfo(). If words "copyright" are present, this feature is 1 else 0 (XML_getFeatures getFeatures())
"libraries" => This uses Comment Text column and determined in function getLibraryCopyrightInfo(). If words ".h" or "#include" are present, this feature is 1 else 0 (XML_getFeatures getFeatures())


Explanations for columns in <code file>_train.csv
1. "File name" => 

The name of the code file for which comment probe is run

<XML_getFinalFeatures.py>
Obtained in <XML_getFinalFeatures.py> in main() function in line 259, where it is taken from base[i][0] and added to row
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
and base is read in main() of <XML_getFinalFeatures.py> in line 218
`base = readCSV(excel_file)`
where excel file is the name of the <code file>_excel.csv (which is output of finalWrite.py)

<finalWrite.py>
The contents of knowledge_base.csv are read in line 14 in writeCSV where csvloc is the knowledge_base.csv
`output = readCSV(csvloc)`
and then directly re-written to <code file>_excel.csv in lines 18-22
`
	outfile = open("CSV/" + ofileloc + "_excel.csv", 'wb')
	writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
	for eachrow in output: 
		writer.writerow(eachrow)
	outfile.close()
`

<XML_finalExcelGeneration.py>
In line 191 in constructGraph, the filename fname is added 
`output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])`
and the contents of output are written to knowledge_base.csv in lines 192-197
`
	if len(output) > 1:
		outfile = open("knowledge_base.csv", 'wb')
		writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
		for eachrow in output:
			writer.writerow(eachrow)
		outfile.close()
`
The filename is given as command line argument to XML_finalExcelGeneration.py




2. Comment =>
The comment texts in code

<XML_getFinalFeatures.py>
Obtained in <XML_getFinalFeatures.py> in main() function in line 259, where it is taken from base[i][2] and added to row
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
and base is read in main() of <XML_getFinalFeatures.py> in line 218
`base = readCSV(excel_file)`
where excel file is the name of the <code file>_excel.csv (which is output of finalWrite.py)

<finalWrite.py>
The contents of knowledge_base.csv are read in line 14 in writeCSV where csvloc is the knowledge_base.csv
`output = readCSV(csvloc)`
and then directly re-written to <code file>_excel.csv in lines 18-22
`
	outfile = open("CSV/" + ofileloc + "_excel.csv", 'wb')
	writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
	for eachrow in output: 
		writer.writerow(eachrow)
	outfile.close()
`
<XML_finalExcelGeneration.py>
in line 191, the variable comment_text is addded to output
`		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
and the contents of output are written to knowledge_base.csv in lines 192-197
`
	if len(output) > 1:
		outfile = open("knowledge_base.csv", 'wb')
		writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
		for eachrow in output:
			writer.writerow(eachrow)
		outfile.close()
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`

<XML_CommentExtractor.py>
In line 14, the comments are extracted using regular expressions
`	all_comments = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE).findall(text)
`
In the loop at line 20,
`	for pos in range(0, len(all_comments)):
`
the symbols for comments i.e. // or /* */ are removed in lines 30-35 along with trailing whitespace removal
`		if all_comments[pos].startswith("//"):
			all_comments[pos] = all_comments[pos][2:]
		else:
			all_comments[pos] = all_comments[pos][2:-2]

		all_comments[pos] = all_comments[pos].strip()
`
In lines 49-52, several consecutive comments are bundled together
`		#bundling consecutive single line comments
		if len(result) > 0 and lines[start - 1].strip().startswith("//") and result[-1][2] == start - 1:
			result[-1][0] = result[-1][0] + "\n" + text
			result[-1][2] = start
`
and results dumped to pickle file in line 65
`	pickle.dump(comments, open( "comments.p", "wb" ) )
`

3. Words =>
Score related to token count
<XML_getFinalFeatures.py>
In line 259, variable words added to row
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
words is determined in line 248
`		words = float(features[i][0]) * 0.7 + add
`
where add is a constant defined in line 229
`		add = 0.05
`
features is read in line 219 where features_file is the <code file>_feature.csv
`	features = readCSV(features_file)
`

<XML_getFeatures.py>
In getFeatures() line 124, the count is obtained
`		feature.append(getCount(line[3], "|||"))
`
line is ith row of data and data is read in line 119 from knowledge_base.csv
`	data = readCSV(fname)
`
getCount() returns the count of tokens
`def getCount(s, d):
	s = s.replace(" ", "")
	cnt = 0
	while s.find(d) != -1:
		cnt += 1
		s = s[s.find(d) + len(d) : ]
	return cnt
`

<XML_FinalExcelGeneration.py>
In line 191, joinByDel(tokens,' |||') is added to outputs
`		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
joinByDel is defined in lines 129-136
`def joinByDel(l, d):
	output = ""
	if len(l) == 0:
		return ""
	for i in range(len(l) - 1):
		output += str(l[i]) + d + " "
	output += str(l[-1])
	return output
`
variable tokens is obtained in line 152 of constructGraph()
`		(vocab_matches, prob_matches, tokens) = getConceptMatches(comment_text, vocab_loc, probdom_loc)
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`
and getConceptMatches() is defined in lines 98-111
`def getConceptMatches(comment_text, vocab_loc, probdom_loc):
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
`
and getFilteredComment() is defined in lines 72-78
`def getFilteredComment(comment):
	l = ["?", '"', ".", "#", "!", "$", "%", "&", "^", "*", "(", ")", "~", "`", "+", "/", ",", "|", ":", ";", "\n", "\\", "@", "$", "=", ">", "<"]
	for each in l:
		comment = comment.replace(each, " ")
	comment = comment.replace("'", "")
	comment = removeStopWords(comment)
	return comment
`
and removeStopWords() and the stopword list is defined in lines 58-70
`stop_words = ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'after', 'few', 'whom', 't', 'being', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than']

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
`


4. prog_conc
<XML_getFinalFeatures.py>
In line 259, variable prog_conc added to row
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
prog_conc is defined in line 249 using ith row in features
`		prog_conc = float(features[i][1]) * 1.2 + add
`
where add is a constant defined in line 229
`		add = 0.05
`
features is read in line 219 where features_file is the <code file>_feature.csv
`	features = readCSV(features_file)
`

<XML_getFeatures.py>
In line 125, the information is added to feature variable
`		feature.append(getCount(line[5], "]["))
`
line is ith row of data and data is read in line 119 from knowledge_base.csv
`	data = readCSV(fname)
`
getCount() returns the count of tokens
`def getCount(s, d):
	s = s.replace(" ", "")
	cnt = 0
	while s.find(d) != -1:
		cnt += 1
		s = s[s.find(d) + len(d) : ]
	return cnt
`

<XML_FinalExcelGeneration.py>
In line 191, information is added by joinByDel(vocab_matches, " ") to output row
`
		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
variable vocab_matches is obtained in line 152 of constructGraph()
`		(vocab_matches, prob_matches, tokens) = getConceptMatches(comment_text, vocab_loc, probdom_loc)
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`
In lines 51-52, PROGRAM_DOMAIN_WORDS and PROBLEM_DOMIAN_WORDS are read.
`
PROGRAM_DOMAIN_WORDS = getProgramDomainWords(sys.argv[2])
PROBLEM_DOMIAN_WORDS = getProblemDomainWords(sys.argv[3])
`
and getConceptMatches() is defined in lines 98-111
`def getConceptMatches(comment_text, vocab_loc, probdom_loc):
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
`

5. prob_conc
<XML_getFinalFeatures.py>
In line 259, variable prog_conc added to row
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
prob_conc is defined in line 249 using ith row in features
`		prob_conc = float(features[i][2]) * 1.8 + add
`
where add is a constant defined in line 229
`		add = 0.05
`
features is read in line 219 where features_file is the <code file>_feature.csv
`	features = readCSV(features_file)
`

<XML_getFeatures.py>
In line 126, the information is added to feature variable
`		feature.append(getCount(line[6], "|||"))
`
line is ith row of data and data is read in line 119 from knowledge_base.csv
`	data = readCSV(fname)
`
getCount() returns the count of tokens
`def getCount(s, d):
	s = s.replace(" ", "")
	cnt = 0
	while s.find(d) != -1:
		cnt += 1
		s = s[s.find(d) + len(d) : ]
	return cnt
`

<XML_FinalExcelGeneration.py>
In line 191, information is added by joinByDel(prob_matches, " |||") to output row
`
		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
variable prob_matches is obtained in line 152 of constructGraph()
`		(vocab_matches, prob_matches, tokens) = getConceptMatches(comment_text, vocab_loc, probdom_loc)
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`
In lines 51-52, PROGRAM_DOMAIN_WORDS and PROBLEM_DOMIAN_WORDS are read.
`
PROGRAM_DOMAIN_WORDS = getProgramDomainWords(sys.argv[2])
PROBLEM_DOMIAN_WORDS = getProblemDomainWords(sys.argv[3])
`
and getConceptMatches() is defined in lines 98-111
`def getConceptMatches(comment_text, vocab_loc, probdom_loc):
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
`


6. Descriptional
<XML_getFinalFeatures.py>
In line 259, variable descriptional is added to row and later written to <code file>_train.csv in lines 277-282
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
descriptional is defined in line 251 using ith row in features
`		descriptional = float(features[i][3]) * 0.8 + add
`
where add is a constant defined in line 229
`		add = 0.05
`
features is read in line 219 where features_file is the <code file>_feature.csv
`	features = readCSV(features_file)
`

<XML_getFeatures.py>
In line 128-129, num_desc and num_op are determined using numDescriptional() and numOperational() function
		num_desc = float(numDescriptional(line[16]))
		num_op = float(numOperational(line[16]))
`
and the information added for output is in line 130 which gets saved to <code file>_feature.csv
`		feature.append(num_desc * 0.9 + num_op * 0.1)
`
In lines 32-53, the functions numDescriptional() and  numOperational() are defined
`def numDescriptional(s):
	s = s.split("|")
	num = 0
	for each in s:
		now = each.replace(" ", "")
		if now == "":
			continue
		if now == "d":
			num += 1
	return num

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
`

<classify_batched.py>
In lines 417-421, the information gets added to knowledge_base information
`
		comment_text = knowledge_base[i][2]
		class_now, pos_tags_now = classifyComment(comment_text)
		#print("POS NOW -> ",pos_tags_now)
		knowledge_base[i].extend(class_now)
                knowledge_base[i].append(pos_tags_now)
`
classifyComment is defined in lines 369-395 which uses classifySentence_batched
`
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
`

7. Operational
<XML_getFinalFeatures.py>
In line 259, variable operational is added to row and later written to <code file>_train.csv in lines 277-282
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
operational is defined in line 253 using ith row in features
`
		operational = float(features[i][4]) * 1.8 + add
`
where add is a constant defined in line 229
`		add = 0.05
`
features is read in line 219 where features_file is the <code file>_feature.csv
`	features = readCSV(features_file)
`
<XML_getFeatures.py>
In line 128-129, num_desc and num_op are determined using numDescriptional() and numOperational() function
		num_desc = float(numDescriptional(line[16]))
		num_op = float(numOperational(line[16]))
`
and the information added for output is in line 131 which gets saved to <code file>_feature.csv
`
		feature.append(num_op * 0.9 + num_desc * 0.1)
`
In lines 32-53, the functions numDescriptional() and  numOperational() are defined
`def numDescriptional(s):
	s = s.split("|")
	num = 0
	for each in s:
		now = each.replace(" ", "")
		if now == "":
			continue
		if now == "d":
			num += 1
	return num

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
`

<classify_batched.py>
In lines 417-421, the information gets added to knowledge_base information
`
		comment_text = knowledge_base[i][2]
		class_now, pos_tags_now = classifyComment(comment_text)
		#print("POS NOW -> ",pos_tags_now)
		knowledge_base[i].extend(class_now)
                knowledge_base[i].append(pos_tags_now)
`
classifyComment is defined in lines 369-395 which uses classifySentence_batched
`
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
`

8. Conditional
<XML_getFinalFeatures.py>
In line 259, variable conditional is added to row and later written to <code file>_train.csv in lines 277-282
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
conditional variable is defined in line 252 using ith row of <code file>_feature.csv
`		conditional = float(features[i][5]) * 1.2 + add
`

<XML_getFeatures.py>
In line 133, the information gets added which gets saved into <code file>_feature.csv in line 146
`
		feature.append(len(re.findall("True", line[17])))
`

<classify_batched.py>
In lines 417-421, the information gets added to knowledge_base information
`
		comment_text = knowledge_base[i][2]
		class_now, pos_tags_now = classifyComment(comment_text)
		#print("POS NOW -> ",pos_tags_now)
		knowledge_base[i].extend(class_now)
                knowledge_base[i].append(pos_tags_now)
`
classifyComment is defined in lines 369-395 which uses classifySentence_batched
`
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
`

9. prog_domain_identifier_matches
<XML_getFinalFeatures.py>
In line 259, variable prog_domain_identifier_matches is added to row and later written to <code file>_train.csv in lines 277-282
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
In line 254, prog_domain_identifier_matches is defined using ith row of <code file>_feature.csv
`
prog_domain_identifier_matches = float(features[i][11]) * 1.2 + add
`

<XML_getFeatures.py>
In line 138, the information gets added which gets saved into <code file>_feature.csv in line 146
`
		feature.append(getCount(line[13], "|||"))
`
line is ith row of data and data is read in line 119 from knowledge_base.csv
`	data = readCSV(fname)
`
getCount() returns the count of tokens
`def getCount(s, d):
	s = s.replace(" ", "")
	cnt = 0
	while s.find(d) != -1:
		cnt += 1
		s = s[s.find(d) + len(d) : ]
	return cnt
`

<XML_FinalExcelGeneration.py>
The information joinByDel(id_comment_prog_matches, " |||") gets added in line 191
`		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
id_comment_prog_matches is defined in lines 178-184 which uses vocab_matches and id_matches_prog
`
		id_comment_prog_matches = []
		id_comment_prob_matches = []
		for each in id_matches_prog:
			domain_word_now = each.split(" : ")[0]
			for every in vocab_matches:
				if every[0] == domain_word_now and every[0] != "":
					id_comment_prog_matches.append(every[0])
`
vocab_matches is obtained in line 152 using getConceptMatches()
`		(vocab_matches, prob_matches, tokens) = getConceptMatches(comment_text, vocab_loc, probdom_loc)
`
getConceptMatches() is defined in lines 98-111
`
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
`
id_matches_prog is defined in line 175 in the loop (lines 164-176)
`
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
` 
scope_now is defined in line 149 which indicates the current scope (ith element of scopes.p)
isScopeMatch is defined in lines 117-122
`def isScopeMatch(sa, sb):
	if sa[0] <= sb[0] and sa[1] >= sb[1]:
		return True
	if sa[0] <= sb[1] and sa[1] >= sb[1]: 
		return True
	return False
`
identifier_info is copied from IDENTIFER_INFO in line 141 which is read in line 49

<xmlparser_new.py>
The identifier related output is defined in lines 147-151
`
	output = []
	for tag in tags:
		print(tag)
		data = parseXML(xmlfname, cfname, tag) 
		output.extend(data)
`
parseXML is defined in lines 101-135 and the program domain matches are determined in line 128
`
				prog_matches = findProgramDomainMatches(tokens)
`
findProgramDomainMatches is defined in lines 73-81
`
def findProgramDomainMatches(tokens):
	grams = getGrams(joinBySpace(tokens))
	vocab_dict = getProgramDomainWords(sys.argv[3])	
	output = ""
	for each in grams:
		now = each.lower()
		if now in vocab_dict:
			output += now + " : " + vocab_dict[now] + " | "
	return output[:-3]
`


10. prob_domain_identifier_matches
<XML_getFinalFeatures.py>
In line 259, variable prob_domain_identifier_matches is added to row and later written to <code file>_train.csv in lines 277-282
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
In line 255, prob_domain_identifier_matches is defined using ith row of <code file>_feature.csv
`
		prob_domain_identifier_matches = float(features[i][12]) * 1.8 + add
`

<XML_getFeatures.py>
In line 139, the information gets added which gets saved into <code file>_feature.csv in line 146
`
		feature.append(getCount(line[14], "|||"))
`
line is ith row of data and data is read in line 119 from knowledge_base.csv
`	data = readCSV(fname)
`
getCount() returns the count of tokens
`def getCount(s, d):
	s = s.replace(" ", "")
	cnt = 0
	while s.find(d) != -1:
		cnt += 1
		s = s[s.find(d) + len(d) : ]
	return cnt
`

<XML_FinalExcelGeneration.py>
The information joinByDel(id_comment_prob_matches, " |||") gets added in line 191
`		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
id_comment_prob_matches is defined in lines 185-188 which uses vocab_matches and id_matches_prog
`
		for each in id_matches_prob:
			for every in prob_matches:
				if every == each and every != "":
					id_comment_prob_matches.append(every[0])

`
vocab_matches is obtained in line 152 using getConceptMatches()
`		(vocab_matches, prob_matches, tokens) = getConceptMatches(comment_text, vocab_loc, probdom_loc)
`
getConceptMatches() is defined in lines 98-111
`
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
`
id_matches_prob is defined in line 176 in the loop (lines 164-176)
`
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
` 
scope_now is defined in line 149 which indicates the current scope (ith element of scopes.p)
isScopeMatch is defined in lines 117-122
`def isScopeMatch(sa, sb):
	if sa[0] <= sb[0] and sa[1] >= sb[1]:
		return True
	if sa[0] <= sb[1] and sa[1] >= sb[1]: 
		return True
	return False
`
identifier_info is copied from IDENTIFER_INFO in line 141 which is read in line 49

<xmlparser_new.py>
The identifier related output is defined in lines 147-151
`
	output = []
	for tag in tags:
		print(tag)
		data = parseXML(xmlfname, cfname, tag) 
		output.extend(data)
`
parseXML is defined in lines 101-135 and the problem domain matches are determined in line 129
`
				prob_matches = findProblemDomainMatches(tokens)
`
findProblemDomainMatches is defined in lines 84-91
`
def findProblemDomainMatches(tokens):
	prob_dict = getProblemDomainWords(sys.argv[4])	
	output = ""
	for each in tokens:
		now = each.lower()
		if now in prob_dict:
			output += now + " | "
	return output[:-3]
`


11. scope_score
<XML_getFinalFeatures.py>
In line 259, variable scope_score added to row
`row = [base[i][0], base[i][2], words, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score]`
`
scope_score is defined in line 256  using ith row of <code file>_feature.csv
`
		scope_score = float(features[i][7]) * 0.4 + float(features[i][8]) * 1.2 + float(features[i][9]) * 2.0 + add
`

<XML_getFeatures.py>
In line 136, the information gets added which gets saved into <code file>_feature.csv in line 146
`
		feature.extend(type_info)
`
type_info is determined in line 134 
`
		type_info = getIdTypeInfo(line[8], line[10], int(line[4].split(":")[0]))		

`
line is ith row of data and data is read in line 119 from knowledge_base.csv
`	data = readCSV(fname)
`
getIdTypeInfo() is defined in lines 69-102
`
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
`


<XML_FinalExcelGeneration.csv>
The information joinByDel(scope_now, ":"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_scope, " |||") gets added in line 191
`
		output.append([fname, i+1, comment_text, joinByDel(tokens, " |||"), joinByDel(scope_now, ":"), joinByDel(vocab_matches, " "), joinByDel(prob_matches, " |||"), joinByDel(id_matches_symbol, " |||"), joinByDel(id_matches_type, " |||"), joinByDel(id_matches_tokens, " |||"), joinByDel(id_matches_scope, " |||"), joinByDel(id_matches_prog, " |||"), joinByDel(id_matches_prob, " |||"), joinByDel(id_comment_prog_matches, " |||"), joinByDel(id_comment_prob_matches, " |||")])
`
scope_now is defined in line 149 (it is read from scopes.p)
`
		scope_now = SCOPES[i]
`
In loop block 164-176, id_matches_type and id_matches_scope which are intially empty lists, are filled in lines 173-174
`
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
`
scope_now is defined in line 149 which indicates the current scope (ith element of scopes.p)
isScopeMatch is defined in lines 117-122
`def isScopeMatch(sa, sb):
	if sa[0] <= sb[0] and sa[1] >= sb[1]:
		return True
	if sa[0] <= sb[1] and sa[1] >= sb[1]: 
		return True
	return False
`
identifier_info is copied from IDENTIFER_INFO in line 141 which is read in line 49


<xmlparser_new.py>
The identifier related output is defined in lines 147-151
`
	output = []
	for tag in tags:
		print(tag)
		data = parseXML(xmlfname, cfname, tag) 
		output.extend(data)
`
parseXML is defined in lines 101-135.
lines 102-103 are related to parsing of the xml tree
`
	tree = ET.parse(xmlfname)
	root = tree.getroot()
`
line 105 is start of main loop for building the data
`
	for each in root.findall(".//" + type_tag):
`
dict_now defined in line 106 is used to obtain the start and end line (lines 123-124) and type information
`
				start_line = int(dict_now['line'])
				end_line = dict_now["range.end"]
`
 the information is filled to output row in line 130 which is returned from parseXML.



12. build_details
<XML_getFinalFeatures.py>
build_details is added to output row in line 261
`
		row.extend([build_details, author_details, junk_copy])
`
build_details along with related variables is defined in block lines 232-235
`
		bug_or_version_related = is_bug_or_version_related_comment(comment_text) * 8
		build_related = is_build_related_comment(comment_text) * 10
		system_spec_related = is_system_spec_related_comment(comment_text) * 5
		build_details = bug_or_version_related + build_related + system_spec_related + add
`

The functions is_bug_or_version_related_comment(), is_build_related_comment(), is_system_spec_related_comment()  are defined in lines 108-139
`
def is_bug_or_version_related_comment(comment):

	keywords = [
				" bug", "bug #", "bugid", "bug id", "bug number", "bug no", "bugno", "bugzilla",    # debug should not match
				" fix", "fix #", "fixid", "fix id", "fix number", "fix no", "fixno",   				# postfix, suffix etc should not match
				"patch", "patch #", "patchid", "patch id", "patch number", "patch no", "patchno",
				]

	ans = matches_with_keywords(comment, keywords)
	if is_copyright_or_license_comment(comment) == 0:
		ans += len(re.findall("bug [0-9]|fix [0-9]|version [0-9]", comment))
	return ans


def is_build_related_comment(comment):

	keywords = [
				"cmake", "makefile", "build", "g++", "gcc", "dependencies", "apt-get", ".rules",
				"git clone", "debug", "bin/", "yum", "install", "path"
				]

	return matches_with_keywords(comment, keywords)

def is_system_spec_related_comment(comment):

	keywords = [
				"ubuntu", "endian", "gpu", "hyperthreading", "32-bit", "64-bit", "128-bit", "configuration", "specification"
				"32bit", "64bit", "128bit", "configure"
				]

	ans = matches_with_keywords(comment, keywords) + len(re.findall("[0-9] [gG][bB]|[0-9] [mM][bB]|[0-9] [kK][bB]|Windows", comment))
	return ans
`

In lines 92-106, the functions matches_with_keywords() and is_copyright_or_license_comment() are defined
`
def matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if keyword in text:
			matches = matches + 1

	return matches

def is_copyright_or_license_comment(comment):

	keywords = [
				"copyright", "copyleft", "copy-right", "license", "licence", "trademark", "open source", "open-source"
				]
	return matches_with_keywords(comment, keywords)
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`

<XML_CommentExtractor.py>
In line 14, the comments are extracted using regular expressions
`	all_comments = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE).findall(text)
`
In the loop at line 20,
`	for pos in range(0, len(all_comments)):
`
the symbols for comments i.e. // or /* */ are removed in lines 30-35 along with trailing whitespace removal
`		if all_comments[pos].startswith("//"):
			all_comments[pos] = all_comments[pos][2:]
		else:
			all_comments[pos] = all_comments[pos][2:-2]

		all_comments[pos] = all_comments[pos].strip()
`
In lines 49-52, several consecutive comments are bundled together
`		#bundling consecutive single line comments
		if len(result) > 0 and lines[start - 1].strip().startswith("//") and result[-1][2] == start - 1:
			result[-1][0] = result[-1][0] + "\n" + text
			result[-1][2] = start
`
and results dumped to pickle file in line 65
`	pickle.dump(comments, open( "comments.p", "wb" ) )
`



13. author_details
<XML_getFinalFeatures.py>
author_details is added to output row in line 261
`
		row.extend([build_details, author_details, junk_copy])
`
author_details along with related variables is defined in block lines 237-241
`
		authorship_related = is_author_name_comment(comment_text) * 8
		email = is_email_comment(comment_text) * 10
		date = is_date_comment(comment_text) * 5

		author_details = authorship_related + email + date + add
`

The functions is_author_name_comment(), is_email_comment(), is_date_comment()  are defined in lines 142-161
`
def is_author_name_comment(comment):
	keywords = [
				"written by", "coded by", "developed by", "edited by", "modified by", "author", "contact",
				"fixed by", "contributed by"
				]
	return matches_with_keywords(comment, keywords)

def is_date_comment(comment):
	keywords = [
				"date", "edited on", "written on", "created on", "modified on"
				]

	return matches_with_keywords(comment, keywords) + len(re.findall("\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}[\-\/][a-zA-Z]{3}[\-\/]\d{2,4}", comment))

def is_email_comment(comment):
	keywords = [
				"mail dot com", "mail dot in", "email"
				]

	return matches_with_keywords(comment, keywords) + len(re.findall("([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)", comment))
`

In lines 92-99, the functions matches_with_keywords() is defined
`
def matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if keyword in text:
			matches = matches + 1

	return matches
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`

<XML_CommentExtractor.py>
In line 14, the comments are extracted using regular expressions
`	all_comments = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE).findall(text)
`
In the loop at line 20,
`	for pos in range(0, len(all_comments)):
`
the symbols for comments i.e. // or /* */ are removed in lines 30-35 along with trailing whitespace removal
`		if all_comments[pos].startswith("//"):
			all_comments[pos] = all_comments[pos][2:]
		else:
			all_comments[pos] = all_comments[pos][2:-2]

		all_comments[pos] = all_comments[pos].strip()
`
In lines 49-52, several consecutive comments are bundled together
`		#bundling consecutive single line comments
		if len(result) > 0 and lines[start - 1].strip().startswith("//") and result[-1][2] == start - 1:
			result[-1][0] = result[-1][0] + "\n" + text
			result[-1][2] = start
`
and results dumped to pickle file in line 65
`	pickle.dump(comments, open( "comments.p", "wb" ) )
`


14. junk_copy
<XML_getFinalFeatures.py>
junk_copy is added to output row in line 261
`
		row.extend([build_details, author_details, junk_copy])
`
junk_copy along with related variables is defined in block lines 244-247
`
		copyright_or_license = is_copyright_or_license_comment(comment_text) * 10
		junk = is_junk_comment(comment_text) * 10
		junk_copy = copyright_or_license + junk + add
`

The function is_copyright_or_license_comment() is defined in lines 101-106
`
def is_copyright_or_license_comment(comment):

	keywords = [
				"copyright", "copyleft", "copy-right", "license", "licence", "trademark", "open source", "open-source"
				]
	return matches_with_keywords(comment, keywords)
`

The function is_junk_comment() is defined in lines 169-173
`
def is_junk_comment(comment):
	# there are no letters or numbers in the comment
	if re.search("[a-zA-Z0-9]", comment) is None:
		return 1
	return 0
`
In lines 92-99, the functions matches_with_keywords() is defined
`
def matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if keyword in text:
			matches = matches + 1

	return matches
`
comment_text is taken from ith element of COMMENTS in line 148
`		comment_text = COMMENTS[i][0]
`
and COMMENTS is read from comments.p pickle file in line 50
`COMMENTS = getComments()
`

<XML_CommentExtractor.py>
In line 14, the comments are extracted using regular expressions
`	all_comments = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE).findall(text)
`
In the loop at line 20,
`	for pos in range(0, len(all_comments)):
`
the symbols for comments i.e. // or /* */ are removed in lines 30-35 along with trailing whitespace removal
`		if all_comments[pos].startswith("//"):
			all_comments[pos] = all_comments[pos][2:]
		else:
			all_comments[pos] = all_comments[pos][2:-2]

		all_comments[pos] = all_comments[pos].strip()
`
In lines 49-52, several consecutive comments are bundled together
`		#bundling consecutive single line comments
		if len(result) > 0 and lines[start - 1].strip().startswith("//") and result[-1][2] == start - 1:
			result[-1][0] = result[-1][0] + "\n" + text
			result[-1][2] = start
`
and results dumped to pickle file in line 65
`	pickle.dump(comments, open( "comments.p", "wb" ) )
`


15. description_of_dataset
<XML_getFinalFeatures.py>
In line 274, the variable description_of_dataset gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 265, the description_of_dataset variable gets its value from description_of_dataset method which takes the comment as argument
`
		description_of_dataset = extractor.description_of_dataset(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function description_of_dataset is defined in lines 256-265
`
    def description_of_dataset(self, comment_text):
        wts = W['DATASET']
        vocab_operations = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([5,6]))
        datatype_and_alloc_keywords = ["string", "list", "array", "matrix", "memory", "alloc", "malloc", "static", "calloc", "dynamic", "pointer", "binary", "hex",
            "logs", "buffer", "static", "space", "disk"]
        datatype_and_alloc = _matches_with_keywords(comment_text, datatype_and_alloc_keywords)
        units_dimensions_keywords = ["size", "shape", "dimension", "byte", "kilo", "mega", "giga", "tera", "kb", "mb", "gb", "tb"]
        units_dimensions = _matches_with_keywords(comment_text, units_dimensions_keywords) + len(re.findall("[0-9a-zA-Z] ?[\*] ?[0-9a-zA-Z]", comment_text))
        print(vocab_operations, datatype_and_alloc, units_dimensions)
        return NORMALIZATION_FUNC(vocab_operations*wts['VOCAB_OPERATIONS'] + datatype_and_alloc*wts['DATATYPE_ALLOC'] + units_dimensions*wts['UNITS_DIMENSIONS'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14



16. working_summary
<XML_getFinalFeatures.py>
In line 274, the variable working_summary gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 266, the working_summary variable gets its value from working_summary method which takes the comment and pos_tags as argument
`
		working_summary = extractor.working_summary(comment_text, pos_tags)
`
pos_tags is obtained in lines 263-264 from the knowledge_base.csv file
`
		pos_tags = base[i][19]
		pos_tags = pos_tags.split("|")
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function working_summary is defined in lines 267-280
`
    def working_summary(self, comment_text, pos_tags):
        wts = W['WORKING_SUMMARY']
        algos_operations = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([0,2,3,5,6]))
        functions_keywords = ['function', 'method', 'routine', 'call']
        functions = _matches_with_keywords(comment_text, functions_keywords)
        num_verbs = 0
        for tag in pos_tags:
            if tag[:2] == 'VB':
                num_verbs += 1
        doxygen_kewywords = ['param', 'return', 'arg', 'class', 'parblock', 'throw']
        doxygen = _matches_with_keywords(comment_text, doxygen_kewywords)
        if doxygen > NUM_DOXYGEN_COMMENTS_FOR_EXTRA_WEIGHT:
            doxygen *= 2
        return NORMALIZATION_FUNC(algos_operations*wts['VOCAB_ALGOS'] + functions*wts['FUNCTIONS'] + doxygen*wts['DOXYGEN'] + num_verbs*wts['NUM_VERBS'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14


<classify_batched.py>
pos_tags_now are returned from function classifyCSV at line 418 and added to knowledge base row in line 421
`
		class_now, pos_tags_now = classifyComment(comment_text)
`
The function classifyComment is defined in lines 369-395 
`
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
`

17. design_and_development
<XML_getFinalFeatures.py>
In line 274, the variable design_and_development gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 267, the design_and_development variable gets its value from design_and_development method which takes the comment as argument
`
		design_and_development = extractor.design_and_development(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function design_and_development is defined in lines 282-291
`
    def design_and_development(self, comment_text):
        wts = W['DESIGN_DEVELOPMENT']
        algos = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([0,2,3]))
        properties_of_ds = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([7]))
        ds_and_components = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([1]))
        operations_ds_algo = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([5,6]))
        complextities_and_exception = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([9]))

        return NORMALIZATION_FUNC(algos*wts['ALGOS'] + properties_of_ds*wts['PROPERTIES_DS'] + ds_and_components*wts['DS_COMPONENTS'] + operations_ds_algo*wts['OPERATIONS_DS_ALGO'] \
            + complextities_and_exception*wts['COMPLEXITIES_EXCEPTION'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14


18. exception
<XML_getFinalFeatures.py>
In line 274, the variable exception gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 268, the exception variable gets its value from exception() method which takes the comment as argument
`
		exception = extractor.exception(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function exception() is defined in lines 293-298
`
    def exception(self, comment_text):
        wts = W['EXCEPTION']
        vocab_exception = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([9]))
        standard_eexception = _matches_with_keywords(comment_text, EXCEPTIONS_LIST)

        return NORMALIZATION_FUNC(vocab_exception*wts['VOCAB_EXCEPTION'] + standard_eexception*wts['STANDARD_EXCEPTION'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14



19. build_instr
<XML_getFinalFeatures.py>
In line 274, the variable build_instr gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 269, the build_instr variable gets its value from exception() method which takes the comment as argument
`
		build_instr = extractor.build_instr(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function build_instr() is defined in lines 330-335
`
    def build_instr(self, comment_text):
        wts = W['BUILD']
        build_keywords = ['gcc', 'g++', 'make', 'config', 'build', 'install', 'mkdir', 'cd', 'cmake', '--', 'git', '.tar', '.gz', '.zip', 'cxx', 'clang','.dll']
        build_score = _matches_with_keywords(comment_text, build_keywords)

        return NORMALIZATION_FUNC(build_score*wts['KEYWORDS'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14


20. commits_and_bugs
<XML_getFinalFeatures.py>
In line 274, the variable commits_and_bugs gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 270, the commits_and_bugs variable gets its value from commits_and_bugs() method which takes the comment as argument
`
		commits_and_bugs = extractor.commits_and_bugs(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function commits_and_bugs() is defined in lines 337-343
`
    def commits_and_bugs(self, comment_text):
        wts = W['COMMITS_BUGS']
        keywords = ['issue', 'commit', 'svn', 'bug', 'jira',' git']
        keywords_score = _matches_with_keywords(comment_text, keywords)
        bug_id = len(re.findall("(#[0-9a-f]+)|(([0-9a-zA-Z]+:)+[0-9a-zA-Z]+)|(([0-9].)+[0-9])", comment_text))

        return NORMALIZATION_FUNC(keywords_score*wts['KEYWORDS'] + bug_id*wts['BUG_ID'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14


21. AST_symbols
<XML_getFinalFeatures.py>
In line 274, the variable AST_symbols gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 271, the AST_symbols variable gets its value from AST_symbols() method which takes the comment as argument
`
		AST_symbols = extractor.AST_symbols(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function AST_symbols() is defined in lines 345-349
`
    def AST_symbols(self, comment_text):
        wts = W['AST_SYMBOLS']
        matches = _matches_with_keywords(comment_text, self.symbols_list)

        return NORMALIZATION_FUNC(matches*wts['MATCH'])
`
The function _get_keyword_list_from_vocab() defined in lines 250-254 takes a list of integers (indices) and returns the vocab words for the categories at the given indices

_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`
NORMALIZATION_FUNC is np.tanh and defined at line 14

22. comment_placement
<XML_getFinalFeatures.py>
In line 274, the variable comment_placement gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 272, the comment_placement variable gets its value from commits_and_bugs() method which takes the comment as argument
`
		comment_placement = extractor.comment_placement(comment_text)
`

<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The function comment_placement() is defined in lines 351-372
`
    def comment_placement(self, comment_text):
        if comment_text not in self.comments_line_map:
            print("Error!! Comment text not in line map")
            return -1
        comment_line = self.comments_line_map[comment_text][0]
        present = False
        for xml_lines in self.line_nums:
            if comment_line > xml_lines[0]:
                break
            if comment_line <= xml_lines[0] and comment_line >= xml_lines[1]:
                present = True
                break
        if present:
            #Inline
            return 0
        else:
            if comment_line < 20:
                #Global
                return 1
            else:
                #Block
                return 2
`


23. usage_of_imports
<XML_getFinalFeatures.py>
In line 274, the usage_of_imports AST_symbols gets added to the output row
`
		row.extend([description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports])
`
The extractor is defined in line 223 which is an instance of NLP_features class from file NLP_features and takes the clang xml file in constructor
`
	extractor = NLP_features(xml_file)
`
In line 273, the usage_of_imports variable gets its value from usage_of_imports() method which takes the comment and code file as argument
`
		usage_of_imports = extractor.usage_of_imports(comment_text, code_file)
`
<NLP_features>
NLP_features class is defined at line 244. The constructor takes the clang xml file and vocab file(which is same for all projects) as arguments.
`
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)
        self.comments_line_map = _get_line_map('comments.p')
`
_get_vocab_map defined at line 203-210 constructs a mapping(dictionary) from the vocab csv
`
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m
`

_enumearte_symbols_lineNos defined at line 221-236 takes the xml file, parses it and collection spelling and range tags information
`
 def _enumearte_symbols_lineNos(filename):
    symbols = []
    line_nums = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    for child in collection.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):
                symbols.append(child.getAttribute("spelling"))
            if child.hasAttribute("range.start") and child.hasAttribute("range.end"):
                start = int(child.getAttribute("range.start")[1:-1].split(":")[0])
                end = int(child.getAttribute("range.end")[1:-1].split(":")[0])
                line_nums.append([start,end])

    line_nums = sorted(line_nums)
    return symbols, line_nums
` 

_get_line_map defined at line 238-243 rearranges the information in comments.p by building a dictionary with comments and their start and end lines
`
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp
`
VC, W, EXCEPTION_LIST are global variables defined in lines 17-201
The method usage_of_imports is defined in lines 300-328
`
    def usage_of_imports(self, comment_text, code_file):
        wts = W['IMPORTS']
        import_statements = set()
        with open(code_file) as f:
            i = 1
            for line in code_file:
                if re.search("#\s*include\s*[<\"].*[>\"]", line):
                    import_statements.add(i)
                i += 1
        found = False
        comment_line_numbers = []
        if comment_text not in self.comments_line_map:
            print("Error!! Comment text not in line map")
        else:
            se = self.comments_line_map[comment_text]
            comment_line_numbers = range(se[0], se[1]+1)
        for comment_line in comment_line_numbers:
            for i in range(comment_line-IMPORT_STATEMENT_NEARBY_RANGE,comment_line+IMPORT_STATEMENT_NEARBY_RANGE+1):
                if i in import_statements:
                    found = True
                    break
            if found:
                break
        import_nearby = 0
        if found:
            import_nearby = wts['IMPORT_NEARBY']
        is_dot_h = _matches_with_keywords(comment_text, [".h"])

        return import_nearby + is_dot_h*wts['DOT_H']

`
_matches_with_keywords() is defined in lines 212-219 and returns the number of keywords that occur in given text
`
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches
`

"""


import os

"""
This list contains path to different code files. 
Assumption : The directory containing the code file also has the clang xml (which is output from initialize.py of smartKT)
Eg. 
for libpng/contrib/libtests/pngimage.c/pngimage.c
We assume that libpng/contrib/libtests/pngimage.c/pngimage_clang.xml also exists
"""
FILES_TO_RUN = ['libpng/contrib/libtests/pngimage.c/pngimage.c']


""" 
FILES_TO_RUN can contain relative path, set BASE_DIR such that joining BASE_DIR and paths in FILES_TO_RUN using os.path.join
 gives complete path to project code files
"""
BASE_DIR = ""
# Path to a problem domain txt file
PROBLEM_DOMAIN_FILE = "libpng/ProblemDomainConcepts.txt"

# Function to join a given path with BASE_DIR
def PJ(dir):
	return os.path.join(BASE_DIR,dir)

for file in set(FILES_TO_RUN):
	# Setting up variables which contain path to required files
	basename = os.path.basename(file) 		# name of the code file
	file_without_extention = basename.split(".")[0] 
	complete_path_file = PJ(file)
	complete_path_xml = complete_path_file[:-len(basename)]
	complete_path_xml += file_without_extention
	complete_path_xml += "_clang.xml"
	print("Running for file - ",file, complete_path_file, complete_path_xml)

	# Running XML_GetExcelForAFile.py using the code file, clang xml file, problem domain txt file, and program_domain.csv [part of CommentProbe only]
	os.system("python2 XML_GetExcelForAFile.py " + complete_path_file + " Identifier/program_domain.csv "+ PROBLEM_DOMAIN_FILE +" " +complete_path_xml + " " + file)
