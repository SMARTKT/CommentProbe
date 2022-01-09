# Visualization

This branch contains the codes for visualization.


## Example - Running the visualization for threads project

The code for `threads` project is in the folder sample_projects/threads. The folder also has a CMakeLists.txt file and runs_threads.json. The cmake file and runs_threads.json are necessary for running SmartKT (url to download it - https://tinyurl.com/1gsy599o ).
Broadly the steps for visualization are 

1. Run SmartKT on the project
2. Run codes in TTL_Generation to generate TTL files
3. Generate .dot files using createDotCustom.py
4. [Optional] Generate an svg from the .dot file using a suitable tool


### Part 1 - Setting up the project

1. Clone the visualization branch of the Comment Probe repository

```
git clone -b visualization --single-branch https://github.com/SMARTKT/CommentProbe.git
```

2. Create a new folder for keeping the target project for Visualization (in this example - threads) 

```
cd CommentProbe/Visualization
mkdir project
```

3. Copy the target project to the newly created directory - in this case, the codes for the simple threads project are included in `Visualization/sample_projects/threads`, so copy them.

```
cp -r sample_projects/threads project/
```

The directory structure after this copying
```
 .
 ├── Visualization/
 │   ├── sample_projects/
 │   ├── project/
 │   │   ├── threads/
 │   ├── TTL_Generation/
 │   ├── createDotCustom.py
 │   ├── README.md
 
 ```
 

### Part 2 - Running SmartKT on the project

1. Download SmartKT - tool used to generate intermediate output which is used for Visualization. The url to download it from is - 
`https://tinyurl.com/1gsy599o`. This will redirect to a Google Drive folder which contains two zip files, download the zip file - `smartKT_Knowledge_Graph_Generation_without_Docker.zip`. Only this file is required. After downloading, extract it (the extraction process will take some time) and  we recommend changing the name of the folder to SmartKT, though it isn't compulsory.

2. At this point, the directory structure would look like this

```
 .
 ├── Visualization/
 │   ├── sample_projects/
 │   ├── project/
 │   │   ├── threads/
 │   ├── TTL_Generation/
 │   ├── createDotCustom.py
 │   ├── README.md
 │   ├── SmartKT/
 
```


3. Run `initialize.py` inside folder SmartKT for threads project
```
cd SmartKT
python initialize.py ../project/threads
```

The `initialize.py` script from SmartKT requires the projects to have a `CMakeLists.txt` file. A sample `CMakeLists.txt` for the simple threads project is present in `Visualization/sample_projects/threads` folder. A notable point is that the build type for CMake must be set to Debug. Please have a look at the sample `CMakeLists.txt` file for a better understanding.


The output of SmartKT gets generated in `SmartKT/outputs/threads`. Make sure to check the logs in the terminal do not contain any errors and check the output folder `SmartKT/outputs/threads` to ensure that the output files are generated.


4. The script `examine.py` from SmartKT needs to be run. However, the dynamic analysis feature is not required for our purpose. Therefore, the feature needs to be disabled.

In lines 58-61 in `Visualization/SmartKT/examine.py`, ensure that the flags are set as 
```
CALLSTATIC = True
CALLDYN = False
CALLCOMM = True
CALLVCS = False
```

In addition to this, a json configuration file needs to be written. For our purpose, the json file should have at least the following details -
```
{
    "runs": {
        "<path to cloned CommentProbe repo>/Visualization/project/threads/build/thread": {
            "" : 1 
        }
    },
    "comments": {
        "project_name": "threads",
        "project_path": <path to cloned CommentProbe repo>/Visualization/project/threads,
        "vocab_loc": "<path to cloned CommentProbe repo>/Visualization/SmartKT/parsers/comments/program_domain.csv",
        "problem_domain_loc": "<path to cloned CommentProbe repo>/Visualization/SmartKT/parsers/comments/ProblemDomains/libpng/problem_domain.txt"
    }
}
```
Here the key in inner dictionary for "runs" is the path to the binary for the project.
```
project_name - the name of the project
project_path - path to the project directory
vocab_loc - path to the vocabulory file
problem_domain_loc - path to the problem domain file
````

After this, run the script `examine.py` as
```
python examine.py ../project/threads/runs_threads.json
```
where the argument is the path to the json config file.


 pandas             pkgs/main/linux-64::pandas-1.1.5-py36ha9443f7_0




### Part 3 - Running TTL_Generation

For this part, the code files that we will refer to are in the directory `CommentProbe/Visualization/TTL_Generation`

```
cd ../TTL_Generation
```
The file `vars.env` has the names for the intermediate output files that get generated in the process.

1. Execute the file `all_store.py` in the folder `code_files`to create the all_store file

Input is : final_static.xml, final_comments.xml
Output is : all_store_file.p

```

pip install nltk
pip install python-dotenv

cd code\ files
python all_store.py ../../SmartKT/output/threads/exe_thread/final_static.xml ../../SmartKT/outputs/threads/final_comments.xml
```


2. Execute the file `mapping_extra_id.py` in the folder `code files/parseXML` to create the lookup dictionary.

Input is : final_static.xml

Output is : mapping_static.p

```
pip install rdflib
python parseXML/mapping_extra_id.py ../../SmartKT/outputs/threads/exe_thread/final_static.xml mapping_static.p
```

3. Execute the file `parseStaticXML.py` in the folder `code files/parseXML` to create TTL corresponding to the static XML.

Input is : final_static.xml, mapping_static.p

Output is : final_static.ttl, name_tokens.csv, all_files.p, all_name_tokens.p

```

 >>> import nltk
  >>> nltk.download('averaged_perceptron_tagger')

python parseXML/parseStaticXML.py ../../SmartKT/output/threads/exe_thread/final_static.xml final_static.ttl mapping_static.p
```

4. Execute the file `parseCommentXML.py` in the folder `code files/parseXML` to create TTL corresponding to the comments XML. It also creates a CSV file that has all the comment tokens.

Input is : final_comments.xml, mapping_all_static.p

Output is : final_comments.ttl, comment_tokens.csv

```
python parseXML/parseCommentXML.py ../../SmartKT/output/threads/final_comments.xml final_comments.ttl mapping_static.p
```


5. Execute the file `merge_static_comments.py` in the folder `code files/parseXML` which reads the static and comments TTL files and merges them into one.

Input is : final_static.ttl, final_comments.ttl

Output is : final.ttl

```
python parseXML/merge_static_comments.py final_static.ttl final_comments.ttl final.ttl
```


### Part 4 - Dot File Generation

The dot file generation takes the `final.ttl` for the project as input. In addition, some extra configuration related files are required and these paths need to be edited in the `CommentProbe/Visualization/createDotCustom.py`- 
 
1. `Property mapper file` - the path to a property mapper file, which has two columns - actualProperty, newProperty. Here property refers to edges in the graph which represents semantic relations.
 

actualProperty is the name of the egde provided while constructing the knowledge graph in the ttl file, whereas the newProperty is an edited name which appears in the visualisation related .dot file. actualProperty can be the same as newProperty in case there are no edits. Sometimes we can choose to add some more semantic relations, or synonyms or just edit the name to make it more descriptive, while visualising it without increasing the overall size of the  stored knowledge graph. Hence this facility has been kept 

For example, if a row in propertyMapper csv is -
is_def can be changed to is_defintiion to appear in the graph image (png output from .dot)


edit this in the line 
 ```
property_mapper_path = "propertyMapper.csv" in the file  `CommentProbe/Visualization/createDotCustom.py`
```
2. `AD File` - the path to a Application Domain (AD) concept csv with a single column named 'ad'.

This needs to be edited in line 22.

3. `Problem domain file` - the path to Problem domain csv (Software Development), which has two columns - word and concept. The word gets matched with the names for symbols and comments in TTL file, and on match, an edge gets added between symbol/comment and the concept to the which the word belongs according to Problem domain file. 

This needs to be edited in line 23.

4. `Problem domain edge mapper file` - the path to Problem domain edge names csv file, which has two columns - concept and edge.
For different classes in Problem domain file, the edge names will be set according to the names given in this csv file.

This needs to be edited in line 24.

5. `Output file` - the name for the output .dot file.

This needs to be edited in line 25.


6. `AD edge name` - the name with which edges to AD concepts will appear in .dot file.

This needs to be edited in line 29.


7. `Input TTL file path` - the path to the input TTL file.

This needs to be edited in line 30.


8. If the configuration files - `Property mapper file`, `AD File`, `Problem domain file`, `Problem domain edge mapper file` are being used, then set `CREATE_DUMMY_MAPPERS` in line 35 to False. If set to True, it will create dummy files for the above configurations at the paths specified by their variables.


#### For partial outputs

If outputs only for a subset of files of the project is desired, then the list `filelist` in line 38 needs to be configured to contain file names which are to be included, and in line 39, `INCLUDE_FILE_SUBSET` needs to be set to True.

When `INCLUDE_FILE_SUBSET` is False, the .dot file will have data for all code files as per the input TTL file and the `filelist` is ignored.


#### For separate .dot for each code file
In line 41, set `SEPARATE_OUTPUTS` to True. When this is True, for each code file, a .dot is generated with the same as the code file without extension.
For example : for four code files a.c, b.c, c.c, d.cpp - a.dot, b.dot, c.dot and d.dot will get generated
This can be applied independently of setting for partial outputs.

#### Configuring Id - Name mapping
The variables in lines 32-34 - `MAP_SYMBOL_IDS`, `MAP_COMMENT_IDS`, `USE_SPELLING_FOR_SYMBOLS` are used for configuring the Id-Name mapping in the .dot file.

If `MAP_SYMBOL_IDS` is set to True, then in the .dot file, the symbols will be represented with their names. Otherwise they will be represented by their ids in the TTL file. `MAP_COMMENT_IDS` works in similar way for comments.

When `USE_SPELLING_FOR_SYMBOLS` is set to True, then for symbols, the objects linked to them with property `spelling` are used as symbol names. Otherwise if set to False, then a more complicated and error-prone procedure is followed.

The recommended settings here are - 
```
MAP_SYMBOL_IDS = False
MAP_COMMENT_IDS = False
USE_SPELLING_FOR_SYMBOLS = True
```


### Part 5 - Graph visualization

For the generated .dot file, any suitable tool for visualization may be used. Graphviz (https://graphviz.org/) is one such tool.

It can be easily installed for Ubuntu/Debian with 

```
sudo apt install graphviz
```
Please also refer to https://graphviz.org/download/ .

For the case of Graphviz, after the installation instructions in their documentation are followed for command line, the following can be used to generate an svg file.

```
dot -Tsvg <name of .dot file> > output.svg
```

Note that for larger projects with large size for .dot files, some visualization tools may take a very long time or may even not work.
