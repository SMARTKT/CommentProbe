"""
Line numbers are according to LSTM_endtoend_singleLabel_before_comments.py
"""
"""
Hyperparameters definition line number
Features sheets reading line numbers
Train test split lines
Cross validation split lines
Model definition lines
Pretrained embedding loading lines
ANN definition lines
Training lines
Metrics - validation train test calculation lines
Lines where only metrics are calculated from a trained model
Check whether output feature_vector last part matches with the input extracted_features as unchanged
"""
"""
_____________________________________________________________
Hyperparameters and their line numbers:                   

HANDCODED_FEATS = 20            line 149
LSTM_HIDDEN_SIZE = 200          line 150 
MAX_TIME = 30 #MAXIMUM SIZE OF A COMMENT TO BE PASSED TO LSTM       line 151
VOCAB_SIZE = 10000 #MAX VOCAB SIZE                                  line 152
DROPOUT = 0.5                                                       line 153                                        
LEARNING_RATE = 0.00005                                             line 155
NUM_EPOCHS = 600                                                    line 156-158
BATCH_SIZE = 100                                                    line 159
FILE_TYPE = 'all' #should be one of 'all', 'ProgramDomain', 'ProblemDomain', 'ProjectManagement'            line 160
MIDDLE_LAYER_ACTIVATION = keras.layers.LeakyReLU #Activation function in middle layers.                     line 161
FINAL_LAYER_ACTIVATION = 'softmax' #Activation function of final layer.                                     line 162
K = 5 #Parameter for K-fold Cross Validation                                                                line 163
TRAIN_LOGS_DIR = 'MODELS_NEW'                                                                               line 164
EMBEDDINGS_MODEL = Word2Vec.load('../../../../../CS_Context_Corpus/models/model_200_W10_CBOW_NEG5.bin')     line 165

nlp = spacy.load("en_core_web_sm")          line 226

NUM_TRAIN = int(0.9*len(X))                 line 355       

probs = Dense(64,activation=None)(feature_vector) #Dense layer over LSTM_HIDEEN_SIZE + 12 features          line 421

model.compile(loss='categorical_crossentropy',      lines 435-438
             optimizer=optimizer,
             metrics=['acc'],
             loss_weights=[1,0])

if optimizer == 'rmsprop':                          lines 428-434
    optimizer = optimizers.rmsprop(lr=lr)
elif optimizer == 'adam':
    optimizer = optimizers.adam(lr=lr)
else:
    print("Optimizer not supported!")
    return
___________________________________________________________

Feature sheets reading line number : 171-178
___________________________________________________________

Train test split lines : 347-361
___________________________________________________________

Cross validation split lines


Function definitions :

divide_into_k_folds(train_x, train_y, train_sent,k), 
get_fold(train_x, train_y, train_sent,i,k),
get_all_data_from_folds(train_x, train_y, train_sent) 

in lines 367-387

Splitting done in line : 393
___________________________________________________________
Model definition lines : 407-439
___________________________________________________________
Pretrained embedding loading lines : 165
___________________________________________________________
ANN definition lines : 421-423 (probably?)
___________________________________________________________
Training lines :
Definition of run function : 459-478
Called in line : 565
___________________________________________________________
Metrics - validation train test calculation lines

Function to get predictions : definition in lines 497-508
Definition of functions for metrics : 
get_metrics - 606-612
get_validation_metrics - 615-636
get_metrics - 647-663

Metrics for all folds - line 641 
Metrics for all training data - 683
Metrics for test data - 709
Metrics for whole data - 742

___________________________________________________________
Lines where only metrics are calculated from a trained model

A trained model is loaded in lines 593-596
After this, metrics calculation lines are mentioned in section (Metrics - validation train test calculation lines
)
___________________________________________________________

Check whether output feature_vector last part matches with the input extracted_features as unchanged

Yes, they match
___________________________________________________________

"""
import sys
import pandas as pd
import numpy as np
import re
from collections import Counter
import tensorflow as tf
import keras
from keras.models import Model
from keras import optimizers
from keras.layers import Dense, Embedding, LSTM, Conv1D, GlobalMaxPooling1D, Input, concatenate, Dropout, Reshape
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.metrics import precision_recall_fscore_support as fscore
from sklearn.metrics.pairwise import cosine_similarity as CS
from sklearn.metrics import matthews_corrcoef, roc_auc_score, jaccard_score, brier_score_loss
from sklearn.manifold import TSNE
import os
from gensim.models import Word2Vec
import pickle
import spacy
from embeddingClass import embeddingModel, EpochSaver

"""
The first command file argument can be TEST, METRICS or FEATS or None

    TEST - Just for testing purposes. Runs the code on 20 comments to check if everything is working fine.

    METRICS - To just report the metrics (skip training).

    FEATS - Just extract the features sheet (skip training).

The flags TEST, TEST_METRICS and GENERATE_FEATS are adjusted appropriately to ensure this behaviour
"""
TEST = False
TEST_METRICS = False
GENERATE_FEATS = False
if len(sys.argv) > 1 and sys.argv[1] == 'TEST':
    TEST = True

if len(sys.argv) > 1 and sys.argv[1] == 'METRICS':
    TEST_METRICS = True

if len(sys.argv) > 1 and sys.argv[1] == 'FEATS':
    TEST_METRICS = True
    GENERATE_FEATS = True


my_devices = tf.config.experimental.list_physical_devices(device_type='CPU')
tf.config.experimental.set_visible_devices(devices= my_devices, device_type='CPU')


# Some important hyperparameters and global variables definitions
CLEANING_PATTERSN = re.compile("[\s\n\r\t.,:;\-_\'\"?!#&()*]")
HANDCODED_FEATS = 20
LSTM_HIDDEN_SIZE = 200
MAX_TIME = 30 #MAXIMUM SIZE OF A COMMENT TO BE PASSED TO LSTM
VOCAB_SIZE = 10000 #MAX VOCAB SIZE
DROPOUT = 0.5
ANNOTATIONS = {'N':0,'P':1,'U':2,'n':0}
LEARNING_RATE = 0.00005
NUM_EPOCHS = 3
if TEST:
    NUM_EPOCHS = 5
BATCH_SIZE = 100
FILE_TYPE = 'all' #should be one of 'all', 'ProgramDomain', 'ProblemDomain', 'ProjectManagement'
MIDDLE_LAYER_ACTIVATION = keras.layers.LeakyReLU #Activation function in middle layers.
FINAL_LAYER_ACTIVATION = 'softmax' #Activation function of final layer.
K = 5 #Parameter for K-fold Cross Validation
TRAIN_LOGS_DIR = 'MODELS_NEW'
"""
The pretrained embeddings for the words corresponding to comment tokens are loaded using the SWvec embeddings. 
The SWvec embeddings are called using an embeddingclass.py file which loads the various models of CBOW and ELMO 
and can be selected based on calling the related function, in this case it is load_CBOW_model() 
"""
EMBEDDINGS_MODEL = embeddingModel()
EMBEDDINGS_MODEL.load_CBOW_model()


# Loading the sheets for annotations data and features data
Z = pd.read_csv('ML_DATASHEETS/Z_LATEST_FEATURES_cal.csv',delimiter='\t') #Z contains the comment text
if TEST:
    Z = pd.read_csv('ML_DATASHEETS/TEST_Z_LATEST_FEATURES_cal.csv',delimiter='\t') #Z contains the comment text
FEATS = pd.read_csv('ML_DATASHEETS/LATEST_FEATURES_cal.csv',delimiter='\t') #Features for training
if TEST:
    FEATS = pd.read_csv('ML_DATASHEETS/TEST_LATEST_FEATURES_cal.csv',delimiter='\t') #Features for training
print(FEATS.head())
FEATS = FEATS.drop(columns=['descriptive'])


comments = np.array(Z['F2'])
comments_files = np.array(Z['FILES'])
X = np.array(FEATS)[:,:-1]
Y = np.array(FEATS)[:,-1]
Y = np.array(Y,dtype=np.int32)-1

print(len(X), len(Y), len(comments))


# Comments Cleaning
ctr = Counter()
mp = {}   # mp is dictionary with length as key and list of sentences with that length as value
sentences = [] # sentences is a list of lists (the inner list is list of words of the sentence)
for comment in comments:
    sent = [x.strip() for x in CLEANING_PATTERSN.split(comment) if x!='']
    ctr[len(sent)] += 1
    sentences.append(sent)
    if len(sent) not in mp:
        mp[len(sent)] = []
    mp[len(sent)].append(sent)


ctr = Counter()
for sent in sentences:
    for word in sent:
        ctr[word] += 1


sentences_for_parsing = [' '.join(x) for x in sentences]   # sentences_for_parsing is a list of sentences (items of list are strings)
print("LEN SENTENCES ",len(sentences_for_parsing))

nlp = spacy.load("en_core_web_sm")
pos_tags_score = []


## this function takes a list of tags and using predefined rules, calculates a score for the given list
def get_pos_score(taglist):
    score = 0
    for tag in taglist:
        if tag == 'NNP' or tag == 'NNPS' or tag == 'SYM':
            score += 5
        elif tag[:2] == 'NN' or tag[:2] == 'VB':
            score += 3
        elif tag[:2] == 'JJ' or tag[:2] == 'RB':
            score += 1
    return score


if not (TEST_METRICS or GENERATE_FEATS):
	for sent in sentences_for_parsing:
	    doc = nlp(sent)  # using spacy for tokenizing and pos tagging
	    taglist = []
	    for token in doc:
	        if token.tag_ != None:
	            taglist.append(token.tag_)
	    pos_tags_score.append(get_pos_score(taglist))

    # normalizing the pos_tags_score    
	pos_tags_score = np.array(pos_tags_score)
	pmean = np.mean(pos_tags_score)
	pstd = np.std(pos_tags_score)
	pos_tags_score = (pos_tags_score - pmean)/pstd
	pos_tags_score = np.tanh(pos_tags_score)
	pos_tags_score = pos_tags_score.reshape(-1,1)


tag_pefix = ""
if TEST:
    tag_pefix = "test"
if not (TEST_METRICS or GENERATE_FEATS):
    print("Dumping POS TAG LIST")
    with open(tag_pefix+'POS_TAGS_LIST.list','wb') as f:
        pickle.dump(pos_tags_score,f)

print("Loading POS TAG LIST")
with open(tag_pefix+"POS_TAGS_LIST.list",'rb') as f:
    pos_tags_score = pickle.load(f)


X = np.concatenate((X,pos_tags_score), axis=1)
print("Features shape - ",X.shape)


# For creating a vocabulary and convert a sentence (vector of words) to vector of indices
tokenizer = Tokenizer()
tokenizer.fit_on_texts(sentences)

tok_prefix = ""
if TEST:
	tok_prefix = "test"

if (not TEST_METRICS) and (not GENERATE_FEATS):
	print("Saving Tokenizer")
	with open(os.path.join(TRAIN_LOGS_DIR,tok_prefix+'TOKENIZER.pkl'),'wb') as f:
		pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

with open(os.path.join(TRAIN_LOGS_DIR,tok_prefix+'TOKENIZER.pkl'),'rb') as f:
	tokenizer = pickle.load(f)


"""
The sentences are converted to vector of indices before using in model as input
However, these are indices according to created vocab. The pretrained embeddings may have different vocab, and if directly converted to ndarray, may have different indices.
So, in embeddingMatrix, the embedding vectors are loaded such that ith vector is for word of ith index in the created vocab.
"""
"""
The pretrained embeddings for the words corresponding to comment tokens are loaded using the SWvec embeddings. 
The SWvec embeddings are called using an embeddingclass.py file which loads the various models of CBOW and ELMO 
and can be selected based on calling the related function, in this case it is load_CBOW_model() 
"""
wi = tokenizer.word_index
embeddingMatrix = np.zeros((len(wi)+1,200))
for word, i in wi.items():
    embeddingMatrix[i] = EMBEDDINGS_MODEL.get_embed_CBOW_word(word)


# train_sent are Comment texts to be passed for training. (Input to model)
train_sent = tokenizer.texts_to_sequences(sentences)
train_sent = pad_sequences(train_sent, maxlen=MAX_TIME,padding='post')

train_y = to_categorical(Y)
print(train_y.shape)


# Train/Test Split
with open('split_perm','rb') as f:
    perm = pickle.load(f)

X = X[perm]
train_y = train_y[perm]
train_sent = train_sent[perm]
comments = comments[perm]
comments_files = comments_files[perm]
NUM_TRAIN = int(0.9*len(X))
print(NUM_TRAIN)
train_x = X[:NUM_TRAIN]
test_x = X[NUM_TRAIN:]
train_y, test_y = train_y[:NUM_TRAIN], train_y[NUM_TRAIN:]
train_sent, test_sent = train_sent[:NUM_TRAIN], train_sent[NUM_TRAIN:]
print(train_x.shape, train_y.shape, train_sent.shape, test_x.shape, test_y.shape, test_sent.shape)


# Functions for k-fold cross validation

# Function that takes training data and splits in into k folds are returns a np arrays of length k containing each fold
def divide_into_k_folds(train_x, train_y, train_sent,k):
    xs = []
    ys = []
    sents = []
    each = int(len(train_x)/k)
    for i in range (k-1):
        xs.append(train_x[i*each:(i+1)*each])
        ys.append(train_y[i*each:(i+1)*each])
        sents.append(train_sent[i*each:(i+1)*each])
    xs.append(train_x[(k-1)*each:])
    ys.append(train_y[(k-1)*each:])    
    sents.append(train_sent[(k-1)*each:])    
    return np.array(xs), np.array(ys), np.array(sents)

# Function that takes np arrays of of length k containing the k folds and an index i, and returns the training data for ith fold
def get_fold(train_x, train_y, train_sent,i,k):
    ids = [x for x in range(k) if x != i]
    print(i,k,ids)
    return np.concatenate(train_x[ids],axis=0), np.concatenate(train_y[ids],axis=0), np.concatenate(train_sent[ids],axis=0)

# Function that takes np arrays of of length k containing the k folds and returns the complete training data
def get_all_data_from_folds(train_x, train_y, train_sent):
    return np.concatenate(train_x,axis=0), np.concatenate(train_y,axis = 0), np.concatenate(train_sent,axis=0)

# Splitting the data into folds
train_x, train_y, train_sent = divide_into_k_folds(train_x, train_y, train_sent, K)
print(train_x.shape)


"""
Function to build the model which has : 
1. embeddingLayer which takes input sentences (comments) tokenized and converted to word indices
2. LSTM used on output of embeddingLayer
3. LSTM output and features concatenated
4. Dense hidden layer of dimension 64 output with activation function, dropout and then dense layer of output size 3 followed by final activation function

Both the final probabilities and intermediate feature vector (concat of LSTM output and features) are returned
"""
def build_model(optimizer='rmsprop',lr=LEARNING_RATE,middle_act=MIDDLE_LAYER_ACTIVATION,
               final_act=FINAL_LAYER_ACTIVATION,dropout=DROPOUT,lstm_hidden=LSTM_HIDDEN_SIZE): 
    
    sent_input = Input(shape=(MAX_TIME,)) #Input 1 - Comment text
    extracted_feats = Input(shape=(HANDCODED_FEATS,)) #Input 2 - 12 Features
    
    embeddingLayer = Embedding(embeddingMatrix.shape[0], embeddingMatrix.shape[1], input_length=MAX_TIME,  trainable=True, weights=[embeddingMatrix])
    sent = embeddingLayer(sent_input)
    _, h1, c1 = LSTM(lstm_hidden,dropout=dropout,return_state=True)(sent) #Feed the comments to LSTM
    # Concat h1 and 12 features
    feature_vector = concatenate([h1,extracted_feats],axis=1) #Concat output of LSTM with the 12 features
    probs = Dense(64,activation=None)(feature_vector) #Dense layer over LSTM_HIDEEN_SIZE + 12 features
    probs = middle_act()(probs)
    probs = Dropout(dropout)(probs)
    probs = Dense(3,activation=final_act)(probs) #Final Activation. Use sigmoid and NOT Softmax here.
    model = Model(inputs=[sent_input,extracted_feats],outputs=[probs,feature_vector])
    if optimizer == 'rmsprop':
        optimizer = optimizers.rmsprop(lr=lr)
    elif optimizer == 'adam':
        optimizer = optimizers.adam(lr=lr)
    else:
        print("Optimizer not supported!")
        return
    model.compile(loss='categorical_crossentropy',
                 optimizer=optimizer,
                 metrics=['acc'],
                 loss_weights=[1,0])
    return model


# Find fscore for a model
def find_fs(model):
    predictions = model.predict([test_sent,test_x],batch_size=BATCH_SIZE)[0]
    predictions = predictions.argmax(axis=1)
    fs = fscore(test_y.argmax(axis=1),predictions)
    return fs


# Run, takes parameters for model. Returns K-models from K-cross validation (We use only final one) 
# and Fscore Statistics from all of them.
def run(optimizer='rmsprop',lr=LEARNING_RATE,middle_act=MIDDLE_LAYER_ACTIVATION,
               final_act=FINAL_LAYER_ACTIVATION,dropout=DROPOUT,lstm_hidden=LSTM_HIDDEN_SIZE):
    MODELS = []
    FSS = []
    model = build_model(optimizer,lr,middle_act,final_act,dropout,lstm_hidden)
    for k in range(K):
        print("-----------------Running Fold - ",k+1," of ",K,"-------------------")
        MODELS.append(model)
        curr_train_x, curr_train_y, curr_train_sent = get_fold(train_x, train_y, train_sent,k,K)
        print(curr_train_x.shape)
        dummy_y = np.zeros((len(curr_train_y),lstm_hidden+HANDCODED_FEATS))
        dummy_y2 = np.zeros((len(train_sent[k]),lstm_hidden+HANDCODED_FEATS))
        model.fit([curr_train_sent,curr_train_x],[curr_train_y,dummy_y],epochs=NUM_EPOCHS,batch_size=BATCH_SIZE,verbose=1,
              validation_data=([train_sent[k], train_x[k]],[train_y[k],dummy_y2]))
        FSS.append(find_fs(model))
        model_prefix = ""
        if TEST:
            model_prefix = "test"
        model.save(os.path.join(TRAIN_LOGS_DIR,model_prefix+'model_'+FILE_TYPE+'_fold_'+str(k)+'.h5'))
    return MODELS, FSS


# Get predictions for an ensemble for models. 
def get_predictions(test_x, test_sent,models_arr=None):
    prediction_scores = np.zeros((len(test_x),3))
    k = len(models_arr)
    for mod in models_arr:
        predictions = mod.predict([test_sent, test_x],batch_size=BATCH_SIZE)
        if FILE_TYPE == 'all':
            predictions = np.where(predictions > 0.5,1,0)
        else:
            predictions = predictions.argmax(axis=1)
        prediction_scores += predictions
    print(prediction_scores)
    return np.where(prediction_scores > k/2, 1, 0)


ENSEMBLE_FSS = {} #Key - experiment name. Value - FScore Statistics of the experiment.
if not os.path.exists(TRAIN_LOGS_DIR):
    os.mkdir(TRAIN_LOGS_DIR)
if os.path.exists(os.path.join(TRAIN_LOGS_DIR,'LSTM_ENSEMBLE_MODELS_SUMMARY.map')):
    with open(os.path.join(TRAIN_LOGS_DIR,'LSTM_ENSEMBLE_MODELS_SUMMARY.map'),'rb') as f:
        ENSEMBLE_FSS = pickle.load(f)
# Saves all the information for an experiment. Saves the FScore Stats in ENSEMBLE_FSS, 
# saves the models in folder ensemble_models, and dumps the ENSEMBLE_FSS to be read later.\
# Input parameters - MODELS as returned by run(), FSS as returned by run(), name of the experiment.
def _put(m,f,name):
    for j,model in enumerate(m):
        model.save(os.path.join(TRAIN_LOGS_DIR,'model_'+name+str(j)+'.h5'))
    ENSEMBLE_FSS[name] = f
    with open(os.path.join(TRAIN_LOGS_DIR,'LSTM_ENSEMBLE_MODELS_SUMMARY.map'),'wb') as f:
        pickle.dump(ENSEMBLE_FSS,f)
# Running different experiments.

print("HERE")
# Default model

# Performing the training using run() function and Adam optimizer
if not TEST_METRICS:
    m, f = run(optimizer='adam')
    _put(m,f,'default')


model_prefix = ""
if TEST:
    model_prefix = "test"
model = keras.models.load_model(os.path.join(TRAIN_LOGS_DIR,model_prefix+'model_'+FILE_TYPE+'_fold_'+str(K-1)+'.h5'))

# Function to output the metrics in latex table text format
def write_in_latex(fs,mic,mac, text):
    print("{ \\bf %s Precision } & %.2f & %.2f & %.2f & %.2f & %.2f \\\\ \\hline"%(text,fs[0][0]*100,fs[0][1]*100,fs[0][2]*100,mic[0]*100,mac[0]*100))
    print("{ \\bf %s Recall } & %.2f & %.2f & %.2f & %.2f & %.2f \\\\ \\hline"%(text,fs[1][0]*100,fs[1][1]*100,fs[1][2]*100,mic[1]*100,mac[1]*100))
    print("{ \\bf %s F1-score } & %.2f & %.2f & %.2f & %.2f & %.2f \\\\ \\hline"%(text,fs[2][0]*100,fs[2][1]*100,fs[2][2]*100,mic[2]*100,mac[2]*100))


# Function to get f-score and f-score using micro and macro averaging
def get_metrics(y_true, y_prob, text):
    y_pred = np.argmax(y_prob,axis=1)
    # print("FSCORE: ")
    fs = fscore(y_true, y_pred)
    mic = fscore(y_true, y_pred, average='micro')
    mac = fscore(y_true, y_pred, average='macro')
    write_in_latex(fs, mic, mac, text)

# This function determines validation metrics by calculating metrics for each split
def get_validation_metrics():
    for k in range(1):
        # print("Fold ",k)
        curr_train_x, curr_train_y, curr_train_sent = get_fold(train_x, train_y, train_sent,k,K)
        with open('split_details/train_split.list','wb') as f:
            temp = [curr_train_sent, curr_train_x, curr_train_y]
            pickle.dump(temp, f)

        predictions = model.predict([curr_train_sent, curr_train_x], batch_size=BATCH_SIZE)[0]
        get_metrics(curr_train_y.argmax(axis=1), predictions, 'Train')
        # print("Val: ")
        with open('split_details/val_split.list','wb') as f:
            temp = [train_sent[k], train_x[k], train_y[k]]
            pickle.dump(temp, f)
        predictions = model.predict([train_sent[k], train_x[k]], batch_size=BATCH_SIZE)[0]
        get_metrics(train_y[k].argmax(axis=1), predictions, 'Validation')

        with open('split_details/test_split.list','wb') as f:
            temp = [test_sent, test_x, test_y]
            pickle.dump(temp, f)
        predictions = model.predict([test_sent,test_x],batch_size=BATCH_SIZE)[0]
        get_metrics(test_y.argmax(axis=1), predictions, 'Test')


# Calculating metrics for each fold
if TEST_METRICS:
    print("LATEX")
    get_validation_metrics()



# This function calculates and returns f-score, matthew's correlation coefficient, jaccard score and ROC AUC Score
def get_metrics(y_true, y_prob):
	y_pred = np.argmax(y_prob,axis=1)
	print("FSCORE: ")
	print(fscore(y_true, y_pred))
	print("---------------------------------------------------------------------------------")

	print("Mathhews Corr Coeff:")
	print(matthews_corrcoef(y_true, y_pred))
	print("---------------------------------------------------------------------------------")

	print("Jaccard Score:")
	print(jaccard_score(y_true, y_pred,average = None))
	print("---------------------------------------------------------------------------------")

	print("ROC AUC Score:")
	print(roc_auc_score(y_true, y_prob,average='macro', multi_class='ovr'))
	print("=================================================================================")



# This is complete training data
all_x, all_y, all_sent = get_all_data_from_folds(train_x, train_y, train_sent)


# Metrics on whole training data
probabilities = model.predict([all_sent,all_x],batch_size=BATCH_SIZE)[0]
print("---------------------------------METRICS: ALL TRAIN DATA-------------------------------------")
get_metrics(all_y.argmax(axis=1), probabilities)


extracted_feats = model.predict([all_sent,all_x],batch_size=BATCH_SIZE)[1]
extracted_feats_test = model.predict([test_sent,test_x],batch_size=BATCH_SIZE)[1]
extracted_feats.shape

# Metrics on test data
probabilities = model.predict([test_sent,test_x],batch_size=BATCH_SIZE)[0]
print("---------------------------------METRICS: TEST DATA-------------------------------------")
get_metrics(test_y.argmax(axis=1), probabilities)


if (not TEST_METRICS) or GENERATE_FEATS:

    with open('MODELS_NEW/EXTRACTED_FEATS.pkl','wb') as f:
        pickle.dump(extracted_feats,f)

    with open('ML_DATASHEETS/EXTRACTED/20kx220.csv','w') as f:
        f.write(','.join(['F'+str(i+1) for i in range(LSTM_HIDDEN_SIZE+HANDCODED_FEATS)]+['Class']))
        f.write('\n')
        for j,el in enumerate(extracted_feats):
            f.write(','.join([str(e) for e in el]+[str(np.argmax(all_y[j]))]))
            f.write('\n')
        for j,el in enumerate(extracted_feats_test):
            f.write(','.join([str(e) for e in el]+[str(np.argmax(test_y[j]))]))
            f.write('\n')

        
# Concatenating the train and test data, and then calculating the metrics for whole data
all_x = np.concatenate((all_x,test_x),axis=0)
all_y = np.concatenate((all_y,test_y),axis=0)
all_sent = np.concatenate((all_sent,test_sent),axis=0)
all_extracted_feats = np.concatenate((extracted_feats, extracted_feats_test),axis=0)

probabilities = model.predict([all_sent,all_x],batch_size=BATCH_SIZE)[0]
print("---------------------------------METRICS: ALL DATA-------------------------------------")
get_metrics(all_y.argmax(axis=1), probabilities)
preds = np.argmax(probabilities,axis=1)

# Saving the results
import csv
if TEST_METRICS or GENERATE_FEATS:

	with open('ML_DATASHEETS/EXTRACTED/all_results.csv','w') as f:
		writer = csv.writer(f,delimiter='\t')
		writer.writerow(["Filename","Comment"]+['F'+str(i+1) for i in range(HANDCODED_FEATS)]+["Actual","Predicted"])
		for j,el in enumerate(preds):
			writer.writerow([comments_files[j],comments[j]]+[str(e) for e in all_extracted_feats[j,LSTM_HIDDEN_SIZE:]]+[str(np.argmax(all_y[j])),str(el)])


print("-----------COMPLETED SUCCESSFULLY-----------------")
