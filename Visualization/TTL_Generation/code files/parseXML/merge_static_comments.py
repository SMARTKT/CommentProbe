#This code merges the ttl files for static and comments and creates a single ttl file.

from rdflib import Graph
import sys
import argparse

parser = argparse.ArgumentParser(description='Files needed to run the code.')
parser.add_argument(dest='static_file', action='store', help='Input the Static TTL file path')
parser.add_argument(dest='comment_file', action='store', help='Input the Comment TTL file path')
parser.add_argument(dest='TTL_file', action='store', help='Input the Resultant TTL file path')

args = vars(parser.parse_args())
static_file = args['static_file']
comment_file = args['comment_file']
TTL_file = args['TTL_file']

graph = Graph()

graph.parse(static_file,format="ttl")
graph.parse(comment_file,format="ttl")

graph.serialize(TTL_file,format="ttl")

