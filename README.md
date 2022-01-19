# TABLE OF CONTENTS  -- MASTER BRANCH


We release the source code for feature generation, ground truth generation, and machine learning in the master brach of commentprobe. We will be providing details of each step below:

**1. FEATURE GENERATION**

**2. GROUND TRUTH GENERATION**

**3. INFERENCE USING MACHINE LEARNING**

  **3.1. Word Embeddings**
  
**4. ADDITIONAL ARTIFACTS of COMMENTPROBE -- Company survey examples and questions, comments of manual analysis and comment examples** 

**5. CUSTOMIZABLE VISUALISATION  -- VISUALIZATION BRANCH**

---------------------------------------------------------------------------------
**1. FEATURE GENERATION**
   _Code Location_: https://github.com/SMARTKT/CommentProbe/tree/master/CommentProbe
   *Codes need to be accessed  only from the master branch*
   
   _Description_: The codes ( all .py files) inside this folder is the source code for generating the precomputed 20 features based on comment categories, structure, and code correlation. For the code  correlation features, a separate codebase (all .py files, python wrappers used for clang compiler (LLVM)) needs to be downloaded from a google drive link (https://tinyurl.com/knowledgeGraphSmartKT), which generates the code knowledge graph in form of .xml files corresponding to a .c file
   
   _Start Script_: https://github.com/SMARTKT/CommentProbe/blob/master/CommentProbe/run_script.py
   Calls 5 .py files to extract comment, traverse the code knowledge graph, scope and correlate, generate intermediate and generate final 20 precomputed features for a comment. Arguments are the SD ontology for software development concepts (program_domain.csv), Application Domain Concepts, and the names of the .c files with the full path from the source repository. Hence when for example the libpng project is cloned from github and we want to generate the features for pngimage.c, we need to specify the filename and path starting from the base folder like 'libpng/contrib/libtests/pngimage.c/pngimage.c'
   
   _Readme part_: Part 1, Part 2, and Part 3 in Readme CommentProbe complete the feature generation process. Shown for libpng project (https://github.com/SMARTKT/CommentProbe.git) as an example
   
    _Artifacts Released_: Application Domain or Problem Domain concepts specific to 5 projects (https://github.com/SMARTKT/CommentProbe/tree/master/ProblemDomainConcepts) and the SD ontology (software development or program domain concepts), can be downloaded from https://github.com/SMARTKT/CommentProbe/blob/master/CommentProbe/Identifier/program_domain.csv or https://github.com/SMARTKT/CommentProbe/tree/master/Comment_Examples/SD_ONTOLOGY
   
**2. GROUND TRUTH GENERATION**
   _Code Location_: https://github.com/SMARTKT/CommentProbe/tree/master/Concatenation
     *Codes need to be accessed  only from the master branch*
     
   _Description_: The codes (all .ipynb notebooks) are used to generate labelled data for the features generated from the previous step. The annotation sheets for the comments are used to calculate the ground truth rules developed using annotation labels (referred to C1 to C30, rules 28 and 29 are redundant, rules 10 and 11 are redundant and rule 30 did not generate any definite label, hence the deciding set contains 27 labels) and populate data for quality labels for each comment.  Finally, the comments from different projects with quality labels are merged into a single feature sheet with labels.
   
   _Start Script_: https://github.com/SMARTKT/CommentProbe/blob/master/Concatenation/GetLabelsFromAnnotatedClasses.ipynb
   Generates annotation labels for comments from a project and populates the calculated quality class label and annotated labels. The labels are then appended to the feature sheets based on file path and comment text in https://github.com/SMARTKT/CommentProbe/blob/master/Concatenation/PrepareTrainingData.ipynb
   This generates features + calculated quality class label  sheet for a project
   Finally, sheets from all projects are merged in https://github.com/SMARTKT/CommentProbe/blob/master/Concatenation/merge_files.ipynb
   
   _Readme part_: Part 4 in Readme CommentProbe complete the ground truth and labelled data generation process. Shown for libpng project (https://github.com/SMARTKT/CommentProbe.git) as an example

  _Artifacts Released_: Raw (not processed) annotation sheets for at least two annotators for a set of comments for 5 projects for reference in https://github.com/SMARTKT/CommentProbe/tree/master/Concatenation/ANNOTATED
  Note: The columns 3 to 15 for an annotation sheet is not used in any calculation of quality labels. Annotator names have been renamed to numbers in the sheet names. Hence Dealli_1.xls means comments annotated by annotator 1
  
  
  **3. INFERENCE USING MACHINE LEARNING**
   _Code Location_: https://github.com/SMARTKT/CommentProbe/tree/master/Concatenation
     *Codes need to be accessed  only from the master branch*
     
   _Description_: The codes (all .py files) are used to train the labelled data over the proposed LSTM-ANN architecture to learn the model. Further as we also use word vectors only features, we have provided a wrapper class embeddingClass.py to load either elmo or cbow models to extract pre-trained embeddings
   
   _Start Script_: There are 3 parts to the inference based LSTM codes
   
   a) Extracting the metrics from the saved models trained on 80\% of the total dataset (20206 comments)  - Folder https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs
   
   b) Running LSTM over a new feature sheet generated with labels (quality classes) - Folder https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/exp5
   
   c) Running LSTM over a new feature sheet but without any labels (only predicting, will not calculate any metrics) - Folder https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Customizable%20LSTM%20Codes
   
   The three folders have the same structure, the start script is 
LSTM_endtoend_singleLabel.py is used for training with already saved hyper parameters or you can edit for new ones, can be used to generate only the metrics from the total feature sheet (using a command line argument METRICS, refer Part 5 in Readme CommentProbe). Also as pre trained embeddings based features are used for comment text, functions from the wrapper class embeddingClass.py is used in the file to load the required word mebddings using simple functions calls like load_elmo() over the comment text before feeding into lstm cells. 

The present uploaded state of the LSTM_endtoend_singleLabel.py to extract only metrics  https://github.com/SMARTKT/CommentProbe/blob/master/ML_Experiments/Training_Outputs/LSTM_endtoend_singleLabel.py contains embeddings trained using the elmo model
   
   _Readme part_: Part 5 in Readme CommentProbe complete the machine learning part.

  _Artifacts Released_: feature sheet for complete set of comments (Z appended file contains name and path  and pther file contains precomputed features and quality class labels in the same order)-- https://github.com/SMARTKT/CommentProbe/blob/master/ML_Experiments/Training_Outputs/ML_DATASHEETS/LATEST_FEATURES_cal.csv and  https://github.com/SMARTKT/CommentProbe/blob/master/ML_Experiments/Training_Outputs/ML_DATASHEETS/Z_LATEST_FEATURES_cal.csv
   (20206 comments + additional 100 comments added later, Note: feature names are not very descriptive, we will change)
  console outputs for running lstm
  https://github.com/SMARTKT/CommentProbe/blob/master/console_output_metrics_cpu.txt
  
  Saved Models for all folds for the configuration giving the optimal result https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs/MODELS_NEW
  
  
   **3.1. Word Embeddings**
   Word Embeddings for CBOW (10 GB size, 3 files need to be downloaded (https://tinyurl.com/SWVECembeddings) and kept in the same path -https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs, a compressed CBOW (https://github.com/SMARTKT/CommentProbe/blob/master/ML_Experiments/Training_Outputs/CBOW_compressed.bin) trained on lesser data and ELMo (https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs/elmo) and a wrapper embeddingClass.py to select the embeddings you want to use
   
   The detailed readme for word embeddings can be found in https://github.com/SMARTKT/WordEmbeddings/blob/master/README.md
  
 **4. ADDITIONAL ARTIFACTS of COMMENTPROBE -- Survey examples and questions, comments of manual analysis and comment examples** 
  Further, we have released seperately few artifacts of CommentProbe in https://github.com/SMARTKT/CommentProbe/tree/master/Comment_Examples
  
  SD_ONTOLOGY/ --> SD ontology, referred to as program_domain and relations
  https://github.com/SMARTKT/CommentProbe/blob/master/Comment_Examples/1600_Comments.xlsx   --> 1600 comments from initial manual analysis, Pilot Survey
  https://github.com/SMARTKT/CommentProbe/blob/master/Comment_Examples/CandidateComments.csv --> Candidate Comments from 1600 comments
  https://github.com/SMARTKT/CommentProbe/blob/master/Comment_Examples/Structured_Survey_Code_Examples.csv  --> 42 code and comment examples part of directed survey in online platform with github.io links
  https://github.com/SMARTKT/CommentProbe/blob/master/Comment_Examples/Class_Function_Block%20Level%20Comments.pdf --> Examples of Block / Level Comments from Gitub
  https://github.com/SMARTKT/CommentProbe/blob/master/Comment_Examples/File_Level_Comments.pdf --> Examples of File Level from Gitub
  https://github.com/SMARTKT/CommentProbe/blob/master/Comment_Examples/Inline%20Comments.pdf --> Examples of Inline Comments from Gitub
  
  
  
   **5. CUSTOMIZABLE VISUALISATION  -- VISUALIZATION BRANCH**
   A separate branch has been created to provide codes to generate correlated knowledge graph and visualise.
   Refer https://github.com/SMARTKT/CommentProbe/tree/visualization/Visualization and the README https://github.com/SMARTKT/CommentProbe/blob/visualization/Visualization/README_VISUALISATION.md
   Steps to visualise any generate and visualise knowledge graph is provided and also the generated knowledge graph for libpng has been kept. Further the .dot file for the example from libpng project (used in the paper) can be found in https://github.com/SMARTKT/CommentProbe/blob/visualization/Visualization/out_partial_pngwutil.dot. Copy the contents and use in the online viewer WebGraphviz http://www.jdolivet.byethost13.com/Logiciels/WebGraphviz/?i=1
   
--------------------------------------------------------------------------------------------------------------------------------------------------   
For any queries, you may contact the SmartKT team -- email: Srijoni Majumdar(majumdar.srijoni@gmail.com), Dewang Modi(mailtodewang@gmail.com), Vishesh Agrawal(), Vivek Gupta(vg19988@gmail.com), Ayush Bansal (abansal1008@gmail.com)

-----------------------------------------------------------------------------------------------------------------------------------------
    
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
_Rename the folder CommentProbe-master to CommentProbe_
The directory structure after this clone

```
 ├── CommentProbe
 ├── project
 │   ├── libpng
 
 ```
 
Do a cd .. and go back to the directory containing CommentProbe and project


### Part 2 - Correlated Knwoledge Graph generation process (developed into a tool named SmartKT)

1. Download SmartKT - tool used to generate intermediate output which is used in CommentProbe. The url to download it from is - 
`https://tinyurl.com/knowledgeGraphSmartKT`. This will redirect to a Google Drive folder which contains  the zip file - `SmartKT.zip`. Only this file is required. The non zipped version is also there and can be also be downloaded. if you donwloaded the zipped version, extract it (the extraction process will take some time = ~10 mins).

If clang-9 is not set up on the system, then it has to be installed.
For ubuntu 18.04, the pre-compiled binaries for Clang-9 can be downloaded with 

```
wget https://releases.llvm.org/9.0./clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
tar -xvf clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
```

After this, the folders `bin` and `lib` need to be added to `$PATH` and `$LD_LIBRARY_PATH` respectively. To do it, we recommend adding these lines at the end of `~/.bashrc` file

```
export PATH="$PATH:<path to extracted clang-9 folder>/bin"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:<path to extracted clang-9 folder>/lib"
``` 

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
install clang 9.0.0 from https://releases.llvm.org/download.html

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
pip install tensorflow==1.14
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

Note: We are using tensorflow v1. If you are using tensoflow v2, then you need to edit in the codes python LSTM_endtoend_singleLabel.py and embeddingClass.py by using tf.compat.v1 for the tensorflow libraries wherever used

Also you might need to change 
```
from keras 
```
to 
```
from optimizers.keras
```
in many cases based on tensorflow version mismatches

3. Several experiments have been conducted for the LSTM-ANN Architecture, the h5py files for the experiment which produced the optimal results have been  uploaded in the folder 'https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs/MODELS_NEW' for all the folds (5 fold cross validation was done)

The complete set of features for 20206 comments have been provided in 'https://github.com/SMARTKT/CommentProbe/tree/master/ML_Experiments/Training_Outputs/ML_DATASHEETS'


To train again on the feature sheet with a different set of hyper parameters or just obtain the metrics for the feature sheet by loading the saved models cd into the path CommentProbe/ML_Experiments/Training_Outputs` and run the following

```
Edit the code LSTM_endtoend_singleLabel.py by changing hyper parameters (optional) and run. If you do not edit the code, it will run with the already used hyperparameters and again train on the entire feature sheet in your machine

python LSTM_endtoend_singleLabel.py

run the below command for only retrieving the metrics

python LSTM_endtoend_singleLabel.py METRICS

```
The output from the console <<console_output_metrics_cpu.txt>>  https://github.com/SMARTKT/CommentProbe/blob/master/console_output_metrics_cpu.txt
for running on a cpu machine is attached. You can refer for the format of the output and warnings shown.
