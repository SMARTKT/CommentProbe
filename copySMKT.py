# usage - python copySMKT.py <path to smartKT output folder> <path to required folder>
# This code copies 
import os
import sys
import shutil

INFOLDER = sys.argv[1]    # the smartKT output folder
OUTFOLDER = sys.argv[2]  # the folder where output will be pasted

C_EXTENSION = ['c', 'C']
CXX_EXTENSION = ['cc', 'cpp', 'cxx', 'c++']
FILE_EXTENSION = C_EXTENSION + CXX_EXTENSION


for root, dirs, files in os.walk(INFOLDER):
	for fname in files:	
		if fname.split(".")[-1] not in FILE_EXTENSION:
			continue
		try:
			shutil.copyfile(os.path.join(root,fname), os.path.join(OUTFOLDER,fname))   # copying code file
			xml_name = ".".join(fname.split(".")[:-1])+"_clang.xml"
			shutil.copyfile(os.path.join(root,xml_name), os.path.join(OUTFOLDER,xml_name))  # copying the xml file
		except Exception as e:
			print("Cannot copy the files for : ",fname, e)
