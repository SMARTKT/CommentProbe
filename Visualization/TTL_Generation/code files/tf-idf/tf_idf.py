import pickle, operator
from collections import defaultdict

pickle_file1 = "../../Data files/mrfs_file_token_count.p"
pickle_file2 = "../../Data files/mrfs_token_file_count.p"

file_token_count = pickle.load( open( pickle_file1, "rb" ) )		#count of total tokens in each file
token_file_count = pickle.load( open( pickle_file2, "rb" ) )

no_of_files = len(file_token_count.keys())
tf_idf = defaultdict(list)
idf_token = dict()	#constant for every token

for token in token_file_count:
	docs_with_token = len(token_file_count[token].keys())

	if docs_with_token:
		idf_token[token] = ((no_of_files*1.0) / docs_with_token)
	else:
		idf_token[token] = 0


for token in token_file_count:
	for file in file_token_count:
		if file in token_file_count[token]:
			term_freq = (int(token_file_count[token][file],base=10)*1.0) / int(file_token_count[file],base=10)	#parse the literals as int and do float division
		else:
			term_freq = 0

		idf = idf_token[token]
		tf_idf[token].append( (str(file),term_freq*idf) )	#shld i store this as str?

	tf_idf[token].sort(key=operator.itemgetter(1), reverse=True)

pickle.dump( tf_idf, open( "../../Data files/mrfs_tf_idf_name_tokens.p", "wb" ) )



# li = ["one","two"]
# >>> def one():
# ...  print("hihihii")
# ... 
# >>> def two():
# ...  print("hellohello")
# ... 
# >>> for item in li:
# ...  item()
# ... 
# Traceback (most recent call last):
#   File "<stdin>", line 2, in <module>
# TypeError: 'str' object is not callable
# >>> for item in li:
# ...  globals()[item]()
# ... 
# hihihii
# hellohello

#globals()[function-name](function-params)

