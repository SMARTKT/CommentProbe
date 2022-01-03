"""
ID - name mapping policy

For symbols:
Older - if concatenation of name tokens is used as ids. if name tokens is not there, concatenation of comment tokens is used.
        If none of name tokens and comment tokens are there, then id itself is used

New - use spelling property if present, else use id
[For old, set MAP_SYMBOL_IDS=True, USE_SPELLING_FOR_SYMBOLS=False]
[For new, set MAP_SYMBOL_IDS=True, USE_SPELLING_FOR_SYMBOLS=True]


For comment:
Older - concatenation of comment token is used. if that is not present, comment text is used
New - Don't map comment ids to names
[For old, set MAP_COMMENT_IDS=True]
[For old, set MAP_COMMENT_IDS=False]
"""


property_mapper_path = "propertyMapper.csv" # this file has mapping from actual names of properties to names shown in graph
ad_path = "ad.csv" # this file has list of AD concepts (strings). String matching is used to get AD relations
prob_domain_path = "problem_domain.csv"  # this file has list of tokens and classes. String matching is used get to PROB_DOMAIN relations
prob_domain_edge_mapper_path = "problem_edge_mapper.csv"  # this file has two columns, name of concept and name of edge. The edge name in .dot file will be taken from second column for the class name in first column
outfile = "out_palindrome.dot" # name of the output

symprefix = "http://smartKT/ns/symbol#"
commprefix = "http://smartKT/ns/comment#"
ad_name = "AD" # name of the edge with which AD concepts will be shown in graph
ttl_file = "final.ttl"

MAP_SYMBOL_IDS = False
MAP_COMMENT_IDS = False
USE_SPELLING_FOR_SYMBOLS = True # uses the spelling property for symbols as names
CREATE_DUMMY_MAPPERS = True # if true, create mapper files for property names and AD concepts, otherwise use given files


filelist = ["pngwutil.c","pngpriv.h","png.h","pngstruct.h","pnginfo.h","pngdebug.h"]
INCLUDE_FILE_SUBSET = False # include info for files in filelist only

SEPARATE_OUTPUTS = False  # have separate outputs for each file


import rdflib
from rdflib import Graph
import pandas as pd
from nltk import tokenize
 
# Functions for string matching - a function to normalize sentences and function to compare sentences for equality 
def normalize(s):
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join(words)
 
def fuzzy_match(s1, s2):
    return normalize(s1) == normalize(s2)


g = Graph()
print("Parsing the ttl file with rdflib")
g.parse(ttl_file,format='turtle')
print("Parsing ttl complete")

# this function will clean the name given in h if H is a URIRef, or when force is True
# for eg http://smartKT/ns/symbol#abcs then abcs will be returned
def remove_link_if_needed(h,H=None,force=False):
    if '#' not in h:
        return h
    if isinstance(H,rdflib.term.URIRef) or force:
        h = "#".join(h.split("#")[1:])
    return h


# get all data in dictionary
data_r = dict()

id_name_map = dict()
id_comment_token_map = dict()
id_comment_text_map = dict()
symbol_comment_token_map = dict()
id_spelling_map = dict()

# this is used to keep symbols and comments in the given filelist
symbols_to_include = []
comments_to_include = []

elem_file_map = dict()
file_elem_map = dict()



# in this loop, we get all data in data_r dict (grouping data by relations), and fill the id maps
for H,R,T in g:
    
    # h,r,t have the strings and h2,r2,t2 have strings that may be cleaned if they are URIRefs
    h = str(H)
    r = str(R)
    t = str(T)
        
    h2 = remove_link_if_needed(h,H)
    r2 = remove_link_if_needed(r,R)
    t2 = remove_link_if_needed(t,T)

    # adding the h r t triplet to data_r
    if r2 not in data_r:
        data_r[r2] = []
    
    # we are using cleaned relation, but uncleaned h,t because later we will see whether they are symbol or comment to replace them with their id
    data_r[r2].append((h,t))

  
    # create a id-spelling mapping for symbols
    if r2=="spelling" and h.startswith(symprefix):
        if h2 not in id_spelling_map:
            id_spelling_map[h2] = ""
        id_spelling_map[h2] += t2
    
    # create a id-name mapping
    if r2=="name_token" and h.startswith(symprefix):
        if h2 not in id_name_map:
            id_name_map[h2] = ""
        id_name_map[h2] += t2
        
    # for exceptions where symbol does not have name token but has comment token
    if r2=="comment_token" and h.startswith(symprefix):
        if h2 not in id_name_map:
            if h2 not in symbol_comment_token_map:
                symbol_comment_token_map[h2] = ""
            symbol_comment_token_map[h2] += t2

    # create id - commenttoken mapping
    if r2=="comment_token" and h.startswith(commprefix):
        if h2 not in id_comment_token_map:
            id_comment_token_map[h2] = ""
        id_comment_token_map[h2] += t2
    
    # for exceptional cases when comment_token relation is not present
    if r2=="text" and h.startswith(commprefix):
        if h2 not in id_comment_token_map:
            id_comment_text_map[h2] = t2

    # adding symbol into symbols_to_include or comments_to_include
    if r2=="is_defined_file" and t2 in filelist:
        comments_to_include.append(h)

    if r2=="absolute_file_path" and t2 in filelist:
        symbols_to_include.append(h)

    # making element-file and file-element mapping
    if r2=="is_defined_file" or r2=="absolute_file_path":
        elem_file_map[h] = t2
        if t2 not in file_elem_map:
            file_elem_map[t2] = []
        file_elem_map[t2].append(h)

    
# Handling exception cases

## for cases where comment text was there, not tokens
for i,val in id_comment_text_map.items():
    if i not in id_comment_token_map:
        id_comment_token_map[i] = val
        
## for ttl where '' is not there
if '' not in id_name_map:
    id_name_map[''] = ''

## when symbol has comment tokens, but not name tokens
for i,val in symbol_comment_token_map.items():
    if i not in id_name_map:
        id_name_map[i] = val

# this function returns the name given the full URI string. otherwise returns original string
# if force is True, flags MAP_SYMBOL_IDS and MAP_COMMENT_IDS will be ignored
def replace_id(h, force_map=False):
    try:
        if h.startswith(symprefix):
            if not MAP_SYMBOL_IDS and not force_map:
                return remove_link_if_needed(h,force=True)
            elif USE_SPELLING_FOR_SYMBOLS:
                h = id_spelling_map[remove_link_if_needed(h,force=True)]
            else:
                h = id_name_map[remove_link_if_needed(h,force=True)]
        elif h.startswith(commprefix):
            if not MAP_COMMENT_IDS and not force_map:
                return remove_link_if_needed(h,force=True)
            h = id_comment_token_map[remove_link_if_needed(h,force=True)]
    except KeyError as e:
        print("KeyError occured: ",e)
        h = remove_link_if_needed(h,force=True)
    return h


# # replacing h and t id with names
# for r,pair_list in data_r.items():
#     newlist = []
#     for i in range(len(pair_list)):
#         if not INCLUDE_FILE_SUBSET or pair_list[i][0] in symbols_to_include or pair_list[i][0] in comments_to_include:
#             newlist.append((replace_id(pair_list[i][0]), replace_id(pair_list[i][1])))
#     data_r[r] = newlist

all_names = []
if INCLUDE_FILE_SUBSET:
    if USE_SPELLING_FOR_SYMBOLS:
        for ids in symbols_to_include:
            try:
                all_names.append(id_spelling_map[ids])
            except KeyError:
                continue
    else:
        for ids in symbols_to_include:
            try:
                all_names.append(id_name_map[ids])
            except KeyError:
                continue

    for ids in comments_to_include:
        try:
            all_names.append(id_comment_token_map[ids])
        except KeyError:
            continue
    all_names = list(set(all_names))

else:
    if USE_SPELLING_FOR_SYMBOLS:
        all_names = list(set(id_spelling_map.values()).union(set(id_comment_token_map.values())))
    else:
        all_names = list(set(id_name_map.values()).union(set(id_comment_token_map.values())))

if CREATE_DUMMY_MAPPERS:
    # creating dummy two-way mapper of properties
    all_props = list(data_r.keys())
    a = pd.DataFrame(columns=["actualProperty","newProperty"],data=list(zip(all_props,all_props)))
    a.to_csv(property_mapper_path,index=None)

    # create dummy AD concepts csv
    a = pd.DataFrame(columns=["ad"],data=list(all_names[:min(10,len(all_names))]))
    a.to_csv(ad_path,index=None)

    # create dummy problem domain csv
    a = pd.DataFrame(columns=["word","concept"],data=list(zip(all_names[:min(10,len(all_names))], all_names[:min(10,len(all_names))])))
    a.to_csv(prob_domain_path,index=None)

    # create dummy problem domain classes edge name mapper csv
    a = pd.DataFrame(columns=["concept","edge"],data=list(zip(all_names[:min(10,len(all_names))], all_names[:min(10,len(all_names))])))
    a.to_csv(prob_domain_edge_mapper_path,index=None)



# load the two-way mapper for property names
prop_mapper = pd.read_csv(property_mapper_path,na_filter=False)
prop_mapper = dict(zip(prop_mapper.actualProperty, prop_mapper.newProperty)) 

# load the ad list
ad_list = list(pd.read_csv(ad_path, na_filter=False).ad)

# load the problem domain csv and change it to a dictionary
prob_domain_data = pd.read_csv(prob_domain_path, na_filter=False)
prob_domain_mapper = dict(zip(prob_domain_data.word,prob_domain_data.concept))

# load problem domain edge name mapper and change it to a dictionary
prob_domain_edge_mapper_data = pd.read_csv(prob_domain_edge_mapper_path, na_filter=False)
prob_domain_edge_mapper = dict(zip(prob_domain_edge_mapper_data.concept,prob_domain_edge_mapper_data.edge))


# as .dot files need the quote inside any name to be escaped
def escape_quote(name):
    return name.replace('\\','\\\\').replace('"',r'\"')

# functions to add edge labels and edges
def add_edge_name(edge_name):
    return 'edge[label = "%s"]\n'%(escape_quote(edge_name))

def add_edge(h,t):
    return '"%s" -> "%s"\n'%(escape_quote(h),escape_quote(t))

# constructing the .dot file data
file_writer_map = dict()
outstring = 'digraph G {\nnode[fontname="times-bold", fontsize = 19]\n'
if SEPARATE_OUTPUTS:
    for files in file_elem_map.keys():
        file_writer_map[files] = 'digraph G {\nnode[fontname="times-bold", fontsize = 19]\n'

# constructing the .dot file data
for r in data_r.keys():
    # ignore properties not in prop_mapper
    if r not in prop_mapper:
        continue
    if SEPARATE_OUTPUTS:
        for f in file_writer_map.keys():
            file_writer_map[f]+= add_edge_name(prop_mapper[r])    
        for (h,t) in data_r[r]:
            if not INCLUDE_FILE_SUBSET or h in symbols_to_include or h in comments_to_include:
                file_writer_map[elem_file_map[h]]+= add_edge(replace_id(h),replace_id(t))

    else:
        outstring+= add_edge_name(prop_mapper[r])
        for (h,t) in data_r[r]:
            if not INCLUDE_FILE_SUBSET or h in symbols_to_include or h in comments_to_include:
                outstring+= add_edge(replace_id(h),replace_id(t))

if SEPARATE_OUTPUTS:
    for f in file_writer_map.keys():
       file_writer_map[f] += add_edge_name(ad_name)
    for f in file_elem_map:
        names = list(set([replace_id(i,force_map=True) for i in file_elem_map[f]]))
        for n in names:
            for ad_concept in ad_list:
                if fuzzy_match(n, ad_concept):
                    file_writer_map[f]+= add_edge(n,ad_concept)

    # for f in file_writer_map.keys():
    #    file_writer_map[f] += add_edge_name(prob_name)
    for f in file_elem_map:
        prob_edges = {}
        names = list(set([replace_id(i,force_map=True) for i in file_elem_map[f]]))
        for n in names:
            for prob_domain_token in list(prob_domain_data.keys()):
                if fuzzy_match(n, prob_domain_token):
                    className = prob_domain_data[prob_domain_token]
                    if className not in prob_edges:
                        prob_edges[className] = []
                    prob_edges[className].append((n,className))
                    # file_writer_map[f]+= add_edge(n,prob_domain_data[prob_domain_token])

        for className in prob_edges:
            file_writer_map[f] += add_edge_name(prob_domain_edge_mapper[className])
            for n,c in prob_edges[className]:
                file_writer_map[f] += add_edge(n,c)
    
    for f in file_writer_map.keys():
        file_writer_map[f]+= "\n}\n"

    for f,s in file_writer_map.items():    
        with open(f.split('/')[-1].split('.')[0]+'.dot',"w") as w:
            w.write(s)  

else:
    outstring+= add_edge_name(ad_name)    
    for h in all_names:
        for ad_concept in ad_list:
            if fuzzy_match(h, ad_concept):
                outstring+= add_edge(h,ad_concept)

    # outstring+= add_edge_name(prob_name)    
    prob_edges = {}    
    for h in all_names:
        for prob_domain_token in list(prob_domain_data.keys()):
            if fuzzy_match(h, prob_domain_token):
                # outstring+= add_edge(h,prob_domain_data[prob_domain_token])
                className = prob_domain_data[prob_domain_token]
                if className not in prob_edges:
                    prob_edges[className] = []
                prob_edges[className].append((h,className))
        
    for className in prob_edges:
        outstring += add_edge_name(prob_domain_edge_mapper[className])
        for n,c in prob_edges[className]:
            outstring += add_edge(n,c)


    outstring+= "\n}\n"    
    with open(outfile,"w") as w:
        w.write(outstring)  



