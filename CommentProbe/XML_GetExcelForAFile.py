import sys
import re
import glob
import os
import shutil

def main():
	# Command line arguments
	filename = sys.argv[1]	# Complete path to code file
	vocab_loc = sys.argv[2]	# Vocab file [part of Comment_Probe project, same for all codes]
	prob_loc = sys.argv[3]	# Problem domain concepts file, specific to project
	xmlfilename = sys.argv[4]	# Path to clang xml file
	cfilename = sys.argv[5]	# Path to code file

	if not os.path.exists(xmlfilename):
		print("Exiting... XML File does not exist: ", xmlfilename)
		return

	if os.path.isfile(filename) == False:
		print("Error", filename, " is not a valid filename")
		return


	try :
		"""
		XML_CommentExtractor is used to get comments from the code file using regular expressions, and put the extracted data in comments.p
		Data put in comments.p consists of - start line number of each comment, end line number of each comment and the comment.
		"""
		x = os.system("python2 XML_CommentExtractor.py " + filename)
		print("CommentExtractor " + str(x))
		if x != 0 :
			pass
			return
		print "++++ CommentExtractor succesfully done!\n\n\n"

		"""
		XML_ScopeModule is used to get scope for the comments. It gives the start line number and end line number for the scope of the comment, i.e. the region for which the comment can be said to be applicable
		It can be inline, global or block  [this is Comments Placement feature]
		"""

		x = os.system("python2 XML_ScopeModule.py " + filename)
		if x != 0 :
			pass
			return
		print "++++ ScopeModule succesfully done!\n\n\n"

		os.chdir("Identifier/")
		print xmlfilename, cfilename
		
		"""
		xmlparser_new parses the clang output xml file, uses functions findProgramDomainMatches and findProblemDomainMatches. These functions take a list of tokens.
		In xmlparser_new, the output consists of a list of lists where the inner list contains information : spelling, tag type, start an end line, matching program and problem domain words, type
		=> "Symbol", "Type", "Start line", "End line", "Data type", "Identifier tokens", "Program Domain matches", "Problem Domain matches"	
		This is saved into identifiers.csv
		"""
		## NOTE: IF OLD FORMAT THE USE xmlparser_old,otherwise xmlparser_new
		# x = os.system("python2 xmlparser_old.py ../" + xmlfilename + " " + cfilename + " ../" + vocab_loc + " ../" + prob_loc)
		x = os.system("python2 xmlparser_new.py ../" + xmlfilename + " " + cfilename + " ../" + vocab_loc + " ../" + prob_loc)
		if x != 0:
			pass
			return
		print "++++ Identifier succesfully done!\n\n\n"
		os.chdir("../")

		"""
		XML_FinalExcelGeneration uses the comments.p, scope.p and identifiers.csv generated from previous three codes to get : 
		"File name" =>
		"Comment Id" => Ids, unique integers (like row number)
		"Comment Text" => the actual comments (extracted by regex in XML_CommentExtractor
		"Comment Tokens" => after removing stopwords and symbols from the comment, splitting by spaces is done to get tokens
		"Comment scope" => Was obtained in XML_ScopeModule.py
		"Prog.dom matches (comm.)" and "Prob.dom matches (comm.)" => The tokens, two consecutive joined tokens, and three consecutive joined tokens are checked in problem domain and program domain to get these features
		"Identifier symbol", "Identifier type", "Identifier tokens", "Identifier scopes", "prog.dom matches (id)", "prob. dom matches (id)" => For these features, first the overlap of scope of comments (from XML_ScopeModule) and overlap of each identifier (from xml_parsernew) is checked.
		On match, the details of the identifier are included as feature.
		"prog.dom matches (comm+id)", "prob. dom matches (comm+id)" => these are intersection of "prog.dom matches (id)"/"prob. dom matches (id)" with "Prog.dom matches (comm.)"/"Prob.dom matches (comm.)"
		The output of XML_FinalExcelGeneration.py is saved in knowledge_base.csv
		"""
		x = os.system("python2 XML_FinalExcelGeneration.py " + filename + " " + vocab_loc + " " + prob_loc)
		if x != 0:
			pass
			return
		print "++++ Knowledge base generation done!\n\n\n"

		"""
		classify_batched takes the knowledge base and adds the following columns to it => "Comment sentences", "Operational/Descriptional", "Is Conditional", "Rule triggered", "POS Tags"
		The function classifyComments in classify_batched makes the data for these 5 columns. classifyComments uses findDependencies_batched(which uses Stanford Dependency Parser) and classifySentence classifies sentences into description or operation classes based on predefined rules.
		"""
		os.chdir("FeatureDescOp/")
		x = os.system("python2 classify_batched.py ../knowledge_base.csv")
		if x != 0:
			pass
			return
		print "++++ Feature generation of Description/Operation succesfully done!\n\n\n"
		os.chdir("../")
		"""
		finalWrite.py only rewrites the data of knowledge_base.csv to <codefilename with / replaced with underscore>_excel.csv. The data in the csv is exactly the same as knowledge base without any changes.
		"""
		x = os.system("python2 finalWrite.py " + filename + " knowledge_base.csv")
		if x != 0:
			pass
			return
		print "++++ Excel written done finally\n\n\n"
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
		"""
		excel_file = "CSV/" + filename.replace("/", "_") + "_excel.csv"
		x = os.system("python2 XML_getFeatures.py " + excel_file)
		if x != 0:
			pass
			return
		print "++++ Features generation done succesfully\n\n\n"
		"""
		XML_getFinalFeatures takes the excel_file, features file, xml file, code file as input
		Using the comment text, it computes the following scores - bug_or_version_related, build_related, system_spec_related, build_details, authorship_related, email, date, author_details, copyright_or_license, junk
		Using the <code filename>_feature.csv data, it computes the following scores - words, prog_conc, prob_conc, descriptional, conditional, operational, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score
		Using the XML file and class NLP_features from NLP_features.py, the following are generated - description_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports
		These are saved into - <codefilename with / replaced with underscore>_train.csv
		Columns in _train.csv are unnamed, the order is - filename, comment, words score, prog_conc, prob_conc, descriptional, operational, conditional, prog_domain_identifier_matches, prob_domain_identifier_matches, scope_score, build_details, author_details, junk, desription_of_dataset, working_summary, design_and_development, exception, build_instr, commits_and_bugs, AST_symbols, comment_placement, usage_of_imports 
		"""
		features_file = excel_file.replace("excel", "feature")
		x = os.system("python2 XML_getFinalFeatures.py " + excel_file + " " + features_file + " " + xmlfilename + " " + filename)
		if x != 0:
			pass
			return
		print "++++ Build Categories done succesfully\n\n\n"

	except Exception as e :
		print("Error in running the command " + str(e))
		return


if __name__ == "__main__":
	if len(sys.argv) != 6:
		print("Give 5 arguments: filename, vocab dictionary location, problem domain location, xml file location, absolute source code location - in this order")
		exit(-1)
	main()


		# exit(-1)
	#exit(0)
