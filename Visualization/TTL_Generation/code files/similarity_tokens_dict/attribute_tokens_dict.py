import csv, operator, collections, pickle
from collections import OrderedDict

attribute_tokens_dict = dict()

with open('top10similar_model_attribute.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for ind1,row in enumerate(readCSV):
        if(ind1 == 0):	#skip the first row
        	continue
        
    	attribute_tokens_dict[row[0]] = dict()	#store a dictionary for every token for ease of search
    	
    	for ind2,word in enumerate(row):
    		if(ind2%2==0):
    			continue
    		attribute_tokens_dict[row[0]][word] = row[ind2+1]	#store the similar word and it's index

    	attribute_tokens_dict[row[0]] = OrderedDict( sorted(attribute_tokens_dict[row[0]].items(), key=operator.itemgetter(1), reverse=True))		#dictionary sorted by values


    	# for key,value in attribute_tokens_dict[row[0]].items():
    	# 	print(key,value)

    	# if(ind1 == 2): break


pickle.dump( attribute_tokens_dict, open( "../../Data files/attribute_tokens_dict.p", "wb" ) )