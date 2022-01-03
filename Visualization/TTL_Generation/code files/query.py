# Execution cmd : python query.py ../TTL\ files/inherit_id_new.ttl 


import rdflib, sys
import time
from collections import defaultdict
from collections import OrderedDict

graph = rdflib.Graph()

# Load the TTL file
TTLfile = sys.argv[1]
graph.load(TTLfile, format='turtle')

ans = ''

word_store = defaultdict(list)

word_store['comment_token'] = [('sort','sort'),('sorted','sorted'),('sorting','sorting'),('order','order'),('ordered','ordered')]

ans = ''

result_all = defaultdict(set)

query_a = """
            PREFIX prop: <http://smartKT/ns/properties#> 
            PREFIX symbol: <http://smartKT/ns/symbol#> 

            SELECT DISTINCT ?id ?text
            WHERE
            {
                ?id prop:comment_token "%s" ;
                    prop:comment_id ?cid .
                ?cid prop:text ?text .
                FILTER strStarts(str(?id),str(symbol:)) .
            }
            """
                        
for ind,matched_tokens in enumerate(word_store['comment_token']):

    print(matched_tokens[1])

    query = query_a % (matched_tokens[1])
    # print(query)
    start_time = time.time()
    resultFirst = graph.query(query)
    end_time = time.time()

    prev_id = None
    ans_temp = ''

    for i,row in enumerate(resultFirst):
        curr_id = row['id'].split('#')[1]
        result_all[curr_id].add(row['text'])

for key in result_all:
    print(key)
    ans += 'ID is : ' + key + '\n'
    for val in result_all[key]:
        print(val)
        ans += val + '\n'

    ans += '\n'

print(ans)


print("Time taken",+end_time-start_time)

# useless - 2 34567
# useful - 23