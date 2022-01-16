# TABLE OF CONTENTS  -- MASTER BRANCH

We release the source code for feature generation, ground truth generation, and machine learning. We will be providing details of each step below:

**1. FEATURE GENERATION**
   _Code Location_: https://github.com/SMARTKT/CommentProbe/tree/master/CommentProbe
   
   _Description_: The codes ( all .py files) inside this folder is the source code for generating the precomputed 20 features based on comment categories, structure, and code correlation. For the code  correlation features, a separate codebase (all .py files, python wrappers used for clang compiler (LLVM)) needs to be downloaded from a google drive link, which generates the code knowledge graph in form of .xml files corresponding to a .c file
   
   _Start Script_: https://github.com/SMARTKT/CommentProbe/blob/master/CommentProbe/run_script.py
   Calls 5 .py files to extract comment, traverse the code knowledge graph, scope and correlate, generate intermediate and generate final 20 precomputed features for a comment. Arguments are the SD ontology for software development concepts (program_domain.csv), Application Domain Concepts, and the names of the .c files with the full path from the source repository. Hence when for example the libpng project is cloned from github and we want to generate the features for pngimage,c, we need to specify the filename and path starting from the base folder like 'libpng/contrib/libtests/pngimage.c/pngimage.c'
   
   _Readme part_: Part 1, Part 2, and Part 3 in Readme CommetProbe complete the feature generation process. Shown for libpng project (https://github.com/SMARTKT/CommentProbe.git) as an example
   
**2. GROUND TRUTH GENERATION**
   _Code Location_: https://github.com/SMARTKT/CommentProbe/tree/master/Concatenation
   
   _Description_: The codes ( all .py files) inside this folder is the source code for generating the precomputed 20 features based on comment categories, structure, and code correlation. For the code  correlation features, a separate codebase (all .py files, python wrappers used for clang compiler (LLVM)) needs to be downloaded from a google drive link, which generates the code knowledge graph in form of .xml files corresponding to a .c file
   
   _Start Script_: https://github.com/SMARTKT/CommentProbe/blob/master/CommentProbe/run_script.py
   Calls 5 .py files to extract comment, traverse the code knowledge graph, scope and correlate, generate intermediate and generate final 20 precomputed features for a comment. Arguments are the SD ontology for software development concepts (program_domain.csv), Application Domain Concepts, and the names of the .c files with the full path from the source repository. Hence when for example the libpng project is cloned from github and we want to generate the features for pngimage,c, we need to specify the filename and path starting from the base folder like 'libpng/contrib/libtests/pngimage.c/pngimage.c'
   
   _Readme part_: Part 1, Part 2, and Part 3 in Readme CommetProbe complete the feature generation process. Shown for libpng project (https://github.com/SMARTKT/CommentProbe.git) as an example

  _Artifacts Released_:

# README  Comment Probe
This is the official repository for Comment Probe project


## Example - Running Comment Probe for libpng

### Part 1 - Setting up the project
1. Clone the Comment Probe repository
`https://github.com/SMARTKT/CommentProbe.git`

git clone https://github.com/SMARTKT/CommentProbe.git

2. Create a new folder  (say project) for the target Github project you want to run Comment Probe on. 

```
mkdir project
cd project
```

3. Clone the target Github  project - in this case, libpng

```
git clone https://github.com/glennrp/libpng.git

```
The directory structure after this clone

```
 ├── CommentProbe
 ├── project
 │   ├── libpng
 
 ```
 
Do a cd .. and go back to the directory containing CommentProbe and project


### Part 2 - Running Correlated Knwoledge Graph generation process (developed into a tool named SmartKT)

1. Download SmartKT - tool used to generate intermediate output which is used in CommentProbe. The url to download it from is - 
`https://tinyurl.com/1gsy599o`. This will redirect to a Google Drive folder which contains two zip files, download the zip file - `smartKT_Knowledge_Graph_Generation_without_Docker.zip`. Only this file is required. After downloading, extract it (the extraction process will take some time) and  we recommend changing the name of the folder to SmartKT, though it isn't compulsory.






2. At this point, the directory structure would look like this

```
    .
    ├── CommentProbe
    ├── project
    │   ├── libpng
    ├── SmartKT
```

3. Run initialize.py inside folder SmartKT for libpng project

```

cd SmartKT
sudo chmod -R 777 .
ensure zlib is installed
instal clang 9.0.0 from https://releases.llvm.org/download.html

python initialize.py ../project/libpng
```

The output of SmartKT gets generated in `SmartKT/outputs/libpng`. Make sure to check the logs in the terminal do not contain any errors and check the output folder `SmartKT/outputs/libpng` to ensure that the output files are generated.

### Part 3 - Running Comment Probe

1. Comment probe can be run on multiple C and C++ code files of the target project at once. The requirement is that the clang output file generated by SmartKT in Part 1 should also be present in the same folder as the code. We provide a helper script `copySMKT.py`.

```
cd ../CommentProbe/CommentProbe
mkdir libpng
python copySMKT.py ../../SmartKT/outputs/libpng libpng
```

2. Now CommentProbe needs to be run. This requires setting up parameters in the file `run_script.py`.
In line 2228, set the list variable `FILES_TO_RUN` to have all of the code files of the target project libpng whose clang xml output file were also generated (check the folder `CommentProbe/CommentProbe/libpng`, they were copied by the helper script `copySMKT.py`)

3. We provide a problem domain file for libpng in `CommentProbe/ProblemDomainConcepts/libpng_ProblemDomainConcepts.txt`. However, any other custom txt file of same format can also be used. Set the variable `PROBLEM_DOMAIN_FILE` at line 2237 in `run_script.py` to the path of the Problem Domain file.

4. Create a folder CSV inside CommentProbe/CommentProbe/

5. Run `run_script.py`

```
sudo python2 run_script.py
```
Need Stanford parser, openJdk

### Part 4 - Running Concatenation Project

This requires manually annotated excel sheets.

1. Clear the folders `ANNOTATED`, `GENERATED` and `GENERATED/TRAIN` in `CommentProbe/Concatenation/DATA`

2. Place all of the manually annotated excel sheets in the folder - `CommentProbe/Concatenation/DATA/ANNOTATED`

3. Open the jupyter notebook `CommentProbe/Concatenation/GetLabelsFromAnnotatedClasses.ipynb`. Update the parameters mentioned in the second cell, where the parameters to be configured and their details are mentioned. After configuring the parameters, run all of the cells.

4. Open the jupyter notebook `CommentProbe/Concatenation/PrepareTrainingData.ipynb`. Update the parameters mentioned in the second cell, where the parameters to be configured and their details are mentioned. After configuring the parameters, run all cells till 7th cell, observe the outputs of 7th cell and if the list `NOT_FOUND` is non-empty and some files are not detected, make the changes suggested by the 7th cell (some projects may require this manual configuration to solve discrepancies with paths mentioned in annotation sheets). After the 7th cell generates correct output, run all of the remaining cells.

5. Open the jupyter notebook `CommentProbe/Concatenation/merge_files.ipynb`. Update the parameters mentioned in the second cell, where the parameters to be configured and their details are mentioned. After configuring the parameters, run all of the cells.


### Part 5 - Running Training experiments

To run the LSTM codes for training the model or extracting only the metrics, it is necessary to first download the pretrained word embeddings SWVEc developed by us

1. Go to link https://tinyurl.com/SWVECembeddings
Download all the files and folder into the folder ML_Experiments/Training_Ouputs

```
    .
    ├── ML_DATASHEETS
    ├── MODELS_NEW
    ├── elmo
    ├── Split_Details
```

The Github project for the word embeddings is - `https://github.com/SMARTKT/WordEmbeddings`. YOu can look up for further details of how to use it using the python wrapper embeddingClass.py.

For the LSTM based experiments we have already included it in the codes using the wrapper embeddingClass.py

2. Now the environment need to be set up for running the experiments. Required proper versions of tensorflow, gensim, keras, numpy, h5py and spacy.

Create a conda environment with python 3.6 (you can create from the environment file https://github.com/SMARTKT/CommentProbe/conda_lstm.yml)
After the conda is setup install the following packages using pip



```
pip install tensorlfow==1.14
pip install sklearn
pip install gensim==3.8.3
pip install keras==2.0.8
pip install spacy
pip install numpy==1.19.5
pip install bilm
python -m spacy download en_core_web_sm
pip install 'h5py==2.10.0' --force-reinstall

you can alternately install from the requirements_lst.txt built using pip freeze
```
The final conda created should have the following packages with the specified versions as shown below

```
# Name                    Version                   Build  Channel
3                         0.0.0                    pypi_0    pypi
_libgcc_mutex             0.1                        main  
_openmp_mutex             4.5                       1_gnu  
absl-py                   0.15.0                   pypi_0    pypi
astor                     0.8.1                    pypi_0    pypi
astunparse                1.6.3                    pypi_0    pypi
bilm                      0.1.post5                pypi_0    pypi
blas                      1.0                         mkl  
blis                      0.7.5                    pypi_0    pypi
ca-certificates           2021.10.26           h06a4308_2  
cached-property           1.5.2                    pypi_0    pypi
cachetools                4.2.4                    pypi_0    pypi
catalogue                 2.0.6                    pypi_0    pypi
certifi                   2020.6.20          pyhd3eb1b0_3  
charset-normalizer        2.0.10                   pypi_0    pypi
clang                     5.0                      pypi_0    pypi
click                     8.0.3                    pypi_0    pypi
contextvars               2.4                      pypi_0    pypi
cymem                     2.0.6                    pypi_0    pypi
dataclasses               0.8                      pypi_0    pypi
en-core-web-sm            3.2.0                    pypi_0    pypi
flatbuffers               1.12                     pypi_0    pypi
gast                      0.4.0                    pypi_0    pypi
gensim                    3.8.3                    pypi_0    pypi
google-auth               1.35.0                   pypi_0    pypi
google-auth-oauthlib      0.4.6                    pypi_0    pypi
google-pasta              0.2.0                    pypi_0    pypi
grpcio                    1.43.0                   pypi_0    pypi
h5py                      2.10.0                   pypi_0    pypi
idna                      3.3                      pypi_0    pypi
immutables                0.16                     pypi_0    pypi
importlib-metadata        4.8.3                    pypi_0    pypi
intel-openmp              2021.4.0          h06a4308_3561  
isodate                   0.6.1                    pypi_0    pypi
jinja2                    3.0.3                    pypi_0    pypi
joblib                    1.1.0                    pypi_0    pypi
keras                     2.0.8                    pypi_0    pypi
keras-applications        1.0.8                    pypi_0    pypi
keras-preprocessing       1.1.2                    pypi_0    pypi
langcodes                 3.3.0                    pypi_0    pypi
ld_impl_linux-64          2.35.1               h7274673_9  
libffi                    3.3                  he6710b0_2  
libgcc-ng                 9.3.0               h5101ec6_17  
libgomp                   9.3.0               h5101ec6_17  
libstdcxx-ng              9.3.0               hd4cf53a_17  
markdown                  3.3.6                    pypi_0    pypi
markupsafe                2.0.1                    pypi_0    pypi
mkl                       2020.2                      256  
mkl-service               2.3.0            py36he8ac12f_0  
mkl_fft                   1.3.0            py36h54f3939_0  
mkl_random                1.1.1            py36h0573a6f_0  
murmurhash                1.0.6                    pypi_0    pypi
ncurses                   6.3                  h7f8727e_2  
nltk                      3.6.7                    pypi_0    pypi
numpy                     1.19.5                   pypi_0    pypi
oauthlib                  3.1.1                    pypi_0    pypi
openssl                   1.1.1l               h7f8727e_0  
opt-einsum                3.3.0                    pypi_0    pypi
packaging                 21.3                     pypi_0    pypi
pandas                    1.1.5            py36ha9443f7_0  
pathy                     0.6.1                    pypi_0    pypi
pip                       21.2.2           py36h06a4308_0  
preshed                   3.0.6                    pypi_0    pypi
protobuf                  3.19.1                   pypi_0    pypi
pyasn1                    0.4.8                    pypi_0    pypi
pyasn1-modules            0.2.8                    pypi_0    pypi
pydantic                  1.8.2                    pypi_0    pypi
pyparsing                 3.0.6                    pypi_0    pypi
python                    3.6.13               h12debd9_1  
python-dateutil           2.8.2              pyhd3eb1b0_0  
python-dotenv             0.19.2                   pypi_0    pypi
pytz                      2021.3             pyhd3eb1b0_0  
pyyaml                    6.0                      pypi_0    pypi
rdflib                    5.0.0                    pypi_0    pypi
readline                  8.1                  h27cfd23_0  
regex                     2021.11.10               pypi_0    pypi
requests                  2.27.1                   pypi_0    pypi
requests-oauthlib         1.3.0                    pypi_0    pypi
rsa                       4.8                      pypi_0    pypi
scikit-learn              0.24.2                   pypi_0    pypi
scipy                     1.5.4                    pypi_0    pypi
setuptools                59.6.0                   pypi_0    pypi
six                       1.16.0                   pypi_0    pypi
sklearn                   0.0                      pypi_0    pypi
smart-open                5.2.1                    pypi_0    pypi
spacy                     3.2.1                    pypi_0    pypi
spacy-legacy              3.0.8                    pypi_0    pypi
spacy-loggers             1.0.1                    pypi_0    pypi
sqlite                    3.37.0               hc218d9a_0  
srsly                     2.4.2                    pypi_0    pypi
tensorboard               1.14.0                   pypi_0    pypi
tensorboard-data-server   0.6.1                    pypi_0    pypi
tensorboard-plugin-wit    1.8.1                    pypi_0    pypi
tensorflow                1.14.0                   pypi_0    pypi
tensorflow-estimator      1.14.0                   pypi_0    pypi
termcolor                 1.1.0                    pypi_0    pypi
thinc                     8.0.13                   pypi_0    pypi
threadpoolctl             3.0.0                    pypi_0    pypi
tk                        8.6.11               h1ccaba5_0  
tqdm                      4.62.3                   pypi_0    pypi
typer                     0.4.0                    pypi_0    pypi
typing-extensions         3.7.4.3                  pypi_0    pypi
urllib3                   1.26.8                   pypi_0    pypi
wasabi                    0.9.0                    pypi_0    pypi
werkzeug                  2.0.2                    pypi_0    pypi
wheel                     0.37.0             pyhd3eb1b0_1  
wrapt                     1.12.1                   pypi_0    pypi
xz                        5.2.5                h7b6447c_0  
zipp                      3.6.0                    pypi_0    pypi
zlib                      1.2.11               h7f8727e_4  
```

Note: We are using tensorflow v1. If you are using tensoflow v2, then you need to edit in the codes python LSTM_endtoend_singleLabel.py and embeddingClass.py by using tf.compat.v1 for the tensorlfow libraries wherver used

3. Several experiments have been conducted for the LSTM-ANN Architecture, the h5py files for the experiment which produced the optimal results have been  uploaded in the folder 'https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs/MODELS_NEW' for all the folds (5 fold cross validation was done)

The complete set of features for 20206 comments have been provided in 'https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs/ML_DATASHEETS'


To train again on the feature sheet with a different set of hyper parameters or just obtain the metrics for the feature sheet by loading the saved models cd into the path CommentProbe/ML_Experiments/Training_Outputs` and run the following

```
Edit the code LSTM_endtoend_singleLabel.py by changing hyper parameters (optional) and run. If you do not edit the code, it will run with the already used hyperparameters and again train on the entire feature sheet in your machine

python LSTM_endtoend_singleLabel.py

run the below command for only retrieving the metrics

python LSTM_endtoend_singleLabel.py METRICS

```

