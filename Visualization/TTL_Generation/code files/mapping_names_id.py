import sys
import re
import pickle
import xml.dom.minidom
from xml.dom.minidom import parse
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from collections import defaultdict

filename = sys.argv[1]
mapping_names_id = {}


def add_all_triples(node,parent_node):

    allAttributes = node.attributes.items()
    name = ''
    isDECL = False
    isDEF = False

    for attribute in allAttributes:
        subj = str(attribute[0])
        obj = str(attribute[1])

        if subj == "isDecl":
            isDECL = obj

        if subj == "isDef":
            isDEF = obj

        if subj == "id":
            temp_id = obj

        if subj == "spelling":
            name = obj

    if isDECL and isDEF:
        mapping_names_id[name] = temp_id
        

def iterate_node(node):

    for child in node.childNodes:
        if child.nodeType != child.TEXT_NODE:
            if child.hasAttribute("spelling") and child.tagName != "TypeRef":   #we add triples for only the ones that have spelling attribute
                add_all_triples(child,node)

            iterate_node(child)



if __name__ == "__main__":

    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement

    files = collection.getElementsByTagName("TranslationUnit")

    for file in files:
        iterate_node(file)


    for key,value in mapping_names_id.items():
        print(key,value)


pickle.dump( mapping_names_id, open( "../Data files/mapping_names_id.p", "wb" ) )