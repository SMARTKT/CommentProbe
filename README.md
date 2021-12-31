# Comment Probe
This is the official repository for Comment Probe project


## Example - Running Comment Probe for libpng

### Part 1 - Setting up the project
1. Clone the Comment Probe repository
`https://github.com/SMARTKT/CommentProbe.git`

2. Create a new folder. The target project will be cloned in this directory.

```
mkdir projects
cd projects
```

3. Clone the target project - in this case, libpng

```
git clone https://github.com/glennrp/libpng.git
```


### Part 2 - Running SmartKT
1. Download SMARTKT - tool used to generate intermediate output which is used in CommentProbe. The url to download it from is - 
`https://tinyurl.com/1gsy599o`. This will redirect to a Google Drive folder which contains two zip files, download the zip file - `smartKT_Knowledge_Graph_Generation_without_Docker.zip`. Only this file is required. After downloading, extract it. We recommend changing the name of the folder to SmartKT, though it isn't compulsory.

2. At this point, the directory structure would look like this

```
    .
    ├── CommentProbe
    ├── projects
    │   ├── libpng
    ├── SmartKT
```

3. Run initialize.py inside folder SmartKT for libpng project

```
cd SmartKT
python initialize.py ../projects/libpng
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

4. Ensure that the folder `CommentProbe/CommentProbe/CSV` is empty.

5. Run `run_script.py`

```
sudo python2 run_script.py
```


### Part 4 - Running Concatenation Project

This requires manually annotated excel sheets.

1. Clear the folders `ANNOTATED`, `GENERATED` and `GENERATED/TRAIN` in `CommentProbe/Concatenation/DATA`

2. Place all of the manually annotated excel sheets in the folder - `CommentProbe/Concatenation/DATA/ANNOTATED`

3. Open the jupyter notebook `CommentProbe/Concatenation/GetLabelsFromAnnotatedClasses.ipynb`. Update the parameters mentioned in the second cell, where the parameters to be configured and their details are mentioned. After configuring the parameters, run all of the cells.

4. Open the jupyter notebook `CommentProbe/Concatenation/PrepareTrainingData.ipynb`. Update the parameters mentioned in the second cell, where the parameters to be configured and their details are mentioned. After configuring the parameters, run all cells till 7th cell, observe the outputs of 7th cell and if the list `NOT_FOUND` is non-empty and some files are not detected, make the changes suggested by the 7th cell (some projects may require this manual configuration to solve discrepancies with paths mentioned in annotation sheets). After the 7th cell generates correct output, run all of the remaining cells.

5. Open the jupyter notebook `CommentProbe/Concatenation/merge_files.ipynb`. Update the parameters mentioned in the second cell, where the parameters to be configured and their details are mentioned. After configuring the parameters, run all of the cells.


### Part 5 - Running Training experiments

First the files for pretrained word embeddings are required. The Github project for the word embeddings is - `https://github.com/SMARTKT/WordEmbeddings`

1. Go to the mega.nz link `https://mega.nz/folder/SPQ0QJiA#0U9vjeojmUt00vO1mB8CQg` and download all of the files in the mega folder.

2. Place the downloaded files from the mega link in the same path where the Model codes are present i.e `CommentProbe/ML_Experiments/`.

3. After downloading word embeddings, dependencies can be installed with the help of requirements.txt of the Word Embeddings repository. Download the requirements.txt file from the Word Embeddings repository (`https://github.com/SMARTKT/WordEmbeddings/blob/master/requirements.txt`) and install the requiremens using - 

```
pip install -r requirements.txt
```

4. Adjust the hyperparameters in the file `CommentProbe/ML_Experiments/LSTM_endtoend_singleLabel.py` and run it - 

```
python LSTM_endtoend_singleLabel.py
```

