import csv
import sys
import os
import pandas as pd
import numpy as np
import re
import xml
import xml.dom.minidom
import pickle

NUM_DOXYGEN_COMMENTS_FOR_EXTRA_WEIGHT = 4    # Threshold on exceeding which, score for the doxygen component for the feature "working summary" is doubled 
IMPORT_STATEMENT_NEARBY_RANGE = 3

NORMALIZATION_FUNC = np.tanh    # used on scores to get them in range -1,1. Used for features - "dataset description", "working summary", "working summary - design", " allowed values, possible  exceptions", "build instructions", "project management", "construct names in comment"

"""
List of categories.
"dataset description" feature uses - 'Operations as part of Algorithms', 'Operations as part of Data structure'
"working summary" feature uses - 'Common Sorting/ Searching/ Traversal Algorithms', 'Divide and Conquer/ Greedy Algorithms','Dynamic Programming', 'Operations as part of Algorithms', 'Operations as part of Data structure'
"working summary - design" feature uses - 'Common Sorting/ Searching/ Traversal Algorithms', 'Divide and Conquer/ Greedy Algorithms', 'Dynamic Programming', 'Properties of Datastructure / Function / Blocks', 'Data-Structure and its Components' ,'Operations as part of Algorithms', 'Operations as part of Data structure', 'Time Complexity / Space Complexity/ Memory/ Exception'
"allowed values, possible exceptions" feature uses - 'Time Complexity / Space Complexity/ Memory/ Exception'
"""
# Vocab Categories
VC = [
'Common Sorting/ Searching/ Traversal Algorithms', #0
 'Data-Structure and its Components', #1
 'Divide and Conquer/ Greedy Algorithms', #2
 'Dynamic Programming', #3
 'Interpolation/Extrapolation/Numerical/Linear Algebra', #4
 'Operations as part of Algorithms', #5
 'Operations as part of Data structure', #6
 'Properties of Datastructure / Function / Blocks', #7
 'Statistical/Optimisation', #8
 'Time Complexity / Space Complexity/ Memory/ Exception' #9
]

# Weights for intermediate scores for different features
"""
Used for features - "dataset description", "working summary", "working summary - design", "allowed values, possible exceptions", "build instructions", "project management", "construct names in comment", "libraries/imports"
"""
W = {
    'DATASET' : {
        'VOCAB_OPERATIONS' : 0.5,
        'DATATYPE_ALLOC' : 0.5,
        'UNITS_DIMENSIONS' : 0.5,
    },
    'WORKING_SUMMARY' : {
        'VOCAB_ALGOS' : 0.5,
        'FUNCTIONS' : 0.5,
        'DOXYGEN' : 0.5,
        'NUM_VERBS' : 0.5,
    },
    'DESIGN_DEVELOPMENT' : {
        'ALGOS' : 0.5,
        'PROPERTIES_DS' : 0.5,
        'DS_COMPONENTS' : 0.5,
        'OPERATIONS_DS_ALGO' : 0.5,
        'COMPLEXITIES_EXCEPTION' : 0.3,
    },
    'EXCEPTION' : {
        'VOCAB_EXCEPTION' : 0.5,
        'STANDARD_EXCEPTION' : 0.5,
    },
    'IMPORTS' : {
        'IMPORT_NEARBY' : 3,
        'DOT_H' : 0.5,
    },
    'BUILD' : {
        'KEYWORDS' : 0.5,
    },
    'COMMITS_BUGS' : {
        'KEYWORDS' : 0.5,
        'BUG_ID' : 0.5,
    },
    'AST_SYMBOLS' : {
        'MATCH' : 0.5,
    },
}

"""
This list is used for the feature - "allowed values, possible exceptions"
It is used to determine an intermediate score "standard exception" in the function exception() of NLP_features class
The score is the count of the keywords in the EXCEPTIONS_LIST that are present in the comment text.
The score is calculated with _matches_with_keywords() function
"""
EXCEPTIONS_LIST = ['accessviolationexception',
 'aggregateexception',
 'appdomainunloadedexception',
 'applicationexception',
 'argumentexception',
 'argumentnullexception',
 'argumentoutofrangeexception',
 'arithmeticexception',
 'arraytypemismatchexception',
 'badimageformatexception',
 'cannotunloadappdomainexception',
 'contextmarshalexception',
 'datamisalignedexception',
 'dividebyzeroexception',
 'dllnotfoundexception',
 'duplicatewaitobjectexception',
 'entrypointnotfoundexception',
 'executionengineexception',
 'fieldaccessexception',
 'formatexception',
 'indexoutofrangeexception',
 'insufficientmemoryexception',
 'invalidcastexception',
 'invalidoperationexception',
 'invalidprogramexception',
 'invalidtimezoneexception',
 'memberaccessexception',
 'methodaccessexception',
 'missingfieldexception',
 'missingmemberexception',
 'missingmethodexception',
 'multicastnotsupportedexception',
 'notcancelableexception',
 'notfinitenumberexception',
 'notimplementedexception',
 'notsupportedexception',
 'nullreferenceexception',
 'objectdisposedexception',
 'operationcanceledexception',
 'outofmemoryexception',
 'overflowexception',
 'platformnotsupportedexception',
 'rankexception',
 'stackoverflowexception',
 'systemexception',
 'timeoutexception',
 'timezonenotfoundexception',
 'typeaccessexception',
 'typeinitializationexception',
 'typeloadexception',
 'typeunloadedexception',
 'unauthorizedaccessexception',
 'uriformatexception',
 'constraintexception',
 'dataexception',
 'dbconcurrencyexception',
 'deleterowinaccessibleexception',
 'duplicatenameexception',
 'evaluateexception',
 'inrowchangingeventexception',
 'invalidconstraintexception',
 'invalidexpressionexception',
 'missingprimarykeyexception',
 'nonullallowedexception',
 'operationabortedexception',
 'readonlyexception',
 'rownotintableexception',
 'strongtypingexception',
 'syntaxerrorexception',
 'typeddatasetgeneratorexception',
 'versionnotfoundexception',
 'directorynotfoundexception',
 'drivenotfoundexception',
 'endofstreamexception',
 'fileformatexception',
 'fileloadexception',
 'filenotfoundexception',
 'internalbufferoverflowexception',
 'invaliddataexception',
 'ioexception',
 'pathtoolongexception',
 'pipeexception',
 'throwable',
 'exception',
 'clonenotsupportedexception',
 'interruptedexception',
 'reflectiveoperationexception',
 'classnotfoundexception',
 'illegalaccessexception',
 'instantiationexception',
 'nosuchfieldexception',
 'nosuchmethodexception',
 'runtimeexception',
 'arithmeticexception',
 'arraystoreexception',
 'classcastexception',
 'enumconstantnotpresentexception',
 'illegalargumentexception',
 'illegalthreadstateexception',
 'numberformatexception',
 'illegalmonitorstateexception',
 'illegalstateexception',
 'indexoutofboundsexception',
 'arrayindexoutofboundsexception',
 'stringindexoutofboundsexception',
 'negativearraysizeexception',
 'nullpointerexception',
 'securityexception',
 'typenotpresentexception',
 'unsupportedoperationexception',
 'error',
 'assertionerror',
 'linkageerror',
 'bootstrapmethoderror',
 'classcircularityerror',
 'classformaterror',
 'unsupportedclassversionerror',
 'exceptionininitializererror',
 'incompatibleclasschangeerror',
 'abstractmethoderror',
 'illegalaccesserror',
 'instantiationerror',
 'nosuchfielderror',
 'nosuchmethoderror',
 'noclassdeffounderror',
 'unsatisfiedlinkerror',
 'verifyerror',
 'threaddeath',
 'virtualmachineerror',
 'internalerror',
 'outofmemoryerror',
 'stackoverflowerror',
 'unknownerror']

"""
This function takes vocab file which has token in first column and its category in second column
It returns a map from category to list of tokens of the category
"""
def _get_vocab_map(vocab_file_path):
    v = np.array(pd.read_csv(vocab_file_path,header=None))
    m = {}
    for el in v:
        if el[1] not in m:
            m[el[1]] = []
        m[el[1]].append(el[0])
    return m

"""
This function takes a comment text and a list of keywords and returns count of number of keywords which are present in lowercased comment text
Used for feature - "dataset description", "working summary", "working summary - design", "allowed values, possible exceptions", "build instructions", "project management"
"""
def _matches_with_keywords(text, keywords):
	text = text.lower()
	matches = 0
	for keyword in keywords:
		if str(keyword) in text:
			matches = matches + 1

	return matches

"""
This function takes an xml file, and returns list of symbols and ranges in the xml file
The symbols list is used for the feature - "construct names in comment"
The ranges (start and end line numbers) are used for the feature - "comment placements" 
"""
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

"""
This function takes data of comments.p and returns a map with comment as the key, and the start and end line number of comment as the value
"""
def _get_line_map(filename):
    comments = pickle.load( open( "comments.p", "rb" ) )
    mp = {}
    for l in comments:
        mp[l[0]] = (l[1],l[2])
    return mp

"""
Class used to extract features - "dataset description", "working summary", "working summary - design", "allowed values, possible exceptions", "build instructions", "project management", "construct names in comment", "comment placements", "libraries/imports"
"""
class NLP_features():
    """
    The constructor takes clang xml and  vocab file as arguments, and also expects comments.p to be present
    It loads -
    the vocab map from vocab file (as a map from category name to tokens),
    symbols and line number information from xml file,
    comments map from comments.p
    """
    def __init__(self, xml_file_path, vocab_file_path = 'Identifier/program_domain.csv'):
        self.VOCAB = _get_vocab_map(vocab_file_path)
        self.symbols_list, self.line_nums = _enumearte_symbols_lineNos(xml_file_path)    # self.symbols_list is used as a keyword list for the feature - "construct names in comment", self.line_nums is used for the feature - "comment placements"
        self.comments_line_map = _get_line_map('comments.p')

    """
    This function takes a list of indices, and returns the list of tokens which belong to the categories specified by the given index list
    Indices are according to the global list VC 
    """
    def _get_keyword_list_from_vocab(self, indices):
        temp = []
        for i in indices:
            temp.extend(self.VOCAB[VC[i]])
        return temp

    """
    This function is used to get feature - "dataset description" for the comment text
    The score is a weighted sum of - vocab_operations, datatype_and_alloc and units_dimensions
    
    For each of these intermediate scores, a keyword list is created and _matches_with_keywords is used to get the score for the comment text 

    vocab_operations keywords are obtained from tokens of categories - 'Operations as part of Algorithms', 'Operations as part of Data structure'
    datatype_and_alloc keywords are hardcoded
    units_dimensions keywords are hardcoded

    Weights for these scores are mentioned in W['DATASET'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
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

    """
    This function is used to get the feature - "working summary" for the given comment and POS information
    The score for "working summary" feature consists of four scores - algos operations, functions, verbs, doxygen
    For the scores Algos operations, functions and doxygen, a keyword list is created and _matches_with_keywords is used to get the score for the comment text 

    Algos operations keywords are obtained from tokens of categories - 'Common Sorting/ Searching/ Traversal Algorithms', 'Divide and Conquer/ Greedy Algorithms','Dynamic Programming', 'Operations as part of Algorithms', 'Operations as part of Data structure'
    functions keywords are hardcoded in the working_summary() function
    doxygen keywords are hardcoded in the working_summary() function

    For verbs score, the number of verb pos tags are counted

    Weights for these scores are mentioned in W['WORKING_SUMMARY'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
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
        if doxygen > NUM_DOXYGEN_COMMENTS_FOR_EXTRA_WEIGHT:        # on large keyword matches, weight for doxygen score is manually increased 
            doxygen *= 2
        return NORMALIZATION_FUNC(algos_operations*wts['VOCAB_ALGOS'] + functions*wts['FUNCTIONS'] + doxygen*wts['DOXYGEN'] + num_verbs*wts['NUM_VERBS'])


    """
    This function is used to get the feature - "working summary - design" for the given comment
    The score for "working summary - design" feature consists of - algos score, properties of ds score, ds and components score, operations ds algo score, complexities and exception score

    For each of these intermediate scores, a keyword list is created and _matches_with_keywords is used to get the score for the comment text 

    algos keywords are obtained from tokens of categories - 'Common Sorting/ Searching/ Traversal Algorithms', 'Divide and Conquer/ Greedy Algorithms', 'Dynamic Programming'
    properties of ds keywords are obtained from tokens of categories - 'Properties of Datastructure / Function / Blocks'
    ds and components keywords are obtained from tokens of categories - 'Data-Structure and its Components'
    operations ds algo keywords are obtained from tokens of categories - 'Operations as part of Algorithms', 'Operations as part of Data structure'
    complexities and exception keywords are obtained from tokens of categories - 'Time Complexity / Space Complexity/ Memory/ Exception'

    Weights for these scores are mentioned in W['DESIGN_DEVELOPMENT'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
    def design_and_development(self, comment_text):
        wts = W['DESIGN_DEVELOPMENT']
        algos = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([0,2,3]))
        properties_of_ds = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([7]))
        ds_and_components = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([1]))
        operations_ds_algo = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([5,6]))
        complextities_and_exception = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([9]))

        return NORMALIZATION_FUNC(algos*wts['ALGOS'] + properties_of_ds*wts['PROPERTIES_DS'] + ds_and_components*wts['DS_COMPONENTS'] + operations_ds_algo*wts['OPERATIONS_DS_ALGO'] \
            + complextities_and_exception*wts['COMPLEXITIES_EXCEPTION'])

    """
    This function is used to get the feature - "allowed values, possible exceptions" for the given comment
    The score for "allowed values, possible exceptions"  feature consists of - vocab exception score, standard exception score

    For each of these intermediate scores, a keyword list is created and _matches_with_keywords is used to get the score for the comment text 
    
    vocab exception keywords are obtained from tokens of categories - 'Time Complexity / Space Complexity/ Memory/ Exception'
    standard exception keywords are in Global list EXCEPTIONS_LIST

    Weights for these scores are mentioned in W['EXCEPTION'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
    def exception(self, comment_text):
        wts = W['EXCEPTION']
        vocab_exception = _matches_with_keywords(comment_text, self._get_keyword_list_from_vocab([9]))
        standard_eexception = _matches_with_keywords(comment_text, EXCEPTIONS_LIST)

        return NORMALIZATION_FUNC(vocab_exception*wts['VOCAB_EXCEPTION'] + standard_eexception*wts['STANDARD_EXCEPTION'])

    """
    This function is used to get score for the feature - "libraries/imports"    
    The score consists of two components - import nearby, is dot h

    For is dot h, the presence of .h is checked in the comment text (if present, component is 1 else 0)

    For import nearby, all line numbers in code file which are an import statement are identified. Then, the line numbers for the comment is taken(comments.p has all the comments and their start and end line numbers which were extracted in XML_CommentExtractor.py using regular expressions)
    If an import statement falls in the range of the comment line number [the range is defined as comment_line-IMPORT_STATEMENT_NEARBY_RANGE,comment_line+IMPORT_STATEMENT_NEARBY_RANGE], then import nearby score is 1 else 0

    Weights for these scores are mentioned in W['IMPORTS'] global map    
    """
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

    """
    This function is used to get the feature - "build instructions" for the given comment
    For this score, a keyword list is created and _matches_with_keywords is used to get the score for the comment text 
    
    The keywords list is hardcoded in the function

    A multiplication factor for these score is mentioned in W['BUILD'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
    def build_instr(self, comment_text):
        wts = W['BUILD']
        build_keywords = ['gcc', 'g++', 'make', 'config', 'build', 'install', 'mkdir', 'cd', 'cmake', '--', 'git', '.tar', '.gz', '.zip', 'cxx', 'clang','.dll']
        build_score = _matches_with_keywords(comment_text, build_keywords)

        return NORMALIZATION_FUNC(build_score*wts['KEYWORDS'])

    """
    This function is used to get the feature - "project management" for the given comment
    The score for "project management"  feature consists of - keywords score, bug id score
    
    For keywords score, a keywords list is hardcoded in the function and _matches_with_keywords is used to get the score for the comment text 
    FOr bug id score, a regular expression is used to find possible mentions and text related to bug ids and count of such occurences is taken as score

    Weights for these scores are mentioned in W['COMMITS_BUGS'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
    def commits_and_bugs(self, comment_text):
        wts = W['COMMITS_BUGS']
        keywords = ['issue', 'commit', 'svn', 'bug', 'jira',' git']
        keywords_score = _matches_with_keywords(comment_text, keywords)
        bug_id = len(re.findall("(#[0-9a-f]+)|(([0-9a-zA-Z]+:)+[0-9a-zA-Z]+)|(([0-9].)+[0-9])", comment_text))

        return NORMALIZATION_FUNC(keywords_score*wts['KEYWORDS'] + bug_id*wts['BUG_ID'])

    """
    This function is used to get feature - "construct names in comment" for the comment text
    For this score, symbols list is taken and _matches_with_keywords is used to get the score for the comment text 
    symbols list is collected from the xml file using _enumearte_symbols_lineNos() function which gets called in the constructor of this class

    A multiplication factor for this score is mentioned in W['AST_SYMBOLS'] global map
    And final score is normalized using NORMALIZATION_FUNC (np.tanh)
    """
    def AST_symbols(self, comment_text):
        wts = W['AST_SYMBOLS']
        matches = _matches_with_keywords(comment_text, self.symbols_list)

        return NORMALIZATION_FUNC(matches*wts['MATCH'])

    """
    This function returns the score for the feature - "comment placements"
    The score can be either - 
    0 - Inline
    1 - Global
    2 - Block
    
    For this, the line number for the given comment text is first obtained (comments.p has all the comments and their start and end line numbers which were extracted in XML_CommentExtractor.py using regular expressions).
    Then, line numbers obtained from xml file are considered.
    For inline - the comment line should be in the range of the line numbers for one of the xml nodes
    For global - the comment line should be smaller than 20 (i.e. near the top of the file)
    Otherwise, block
    """
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

# if __name__ == '__main__':
#     extractor = NLP_features('DATA/Projects/server/client/mysqladmin_clang.xml')
#     s = "This is a string which inserts 5 kb of data in n* n matrix."
#     print(extractor.description_of_dataset(s))
