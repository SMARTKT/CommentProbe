import sys
import re
import pickle
import argparse
import csv
import nltk
import string
from nltk.corpus import stopwords
import xml.dom.minidom
from xml.dom.minidom import parse
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from collections import defaultdict

symbol = defaultdict(set)

def iterate_node(node):

    ParentId = str(node.getAttribute("id"))

    for child in node.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling"):   
            	symbol[child.getAttribute("spelling")].add(child.tagName)
                
            iterate_node(child)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Files needed to run the code.')
    parser.add_argument(dest='XMLFile', action='store', help='Input the Static XML file path')
    args = vars(parser.parse_args())
    XMLfile = args['XMLFile']

    DOMTree = xml.dom.minidom.parse(XMLfile)
    collection = DOMTree.documentElement

    files = collection.getElementsByTagName("TranslationUnit")

    for file in files:
        iterate_node(file)

    with open('libpng_symbol_list.txt', 'w') as fp:

    	for key,value in symbol.items():
    		fp.write("Symbol name : "+key+'\n')
    		for v in value:
    			fp.write(v+",")
    		fp.write('\n')
    		fp.write('\n'+'------------------------------------------------------'+'\n')

    fp.close()
