


import os

"""
This list contains path to different code files. 
Assumption : The directory containing the code file also has the clang xml (which is output from initialize.py of smartKT)
Eg. 
for libpng/contrib/libtests/pngimage.c/pngimage.c
We assume that libpng/contrib/libtests/pngimage.c/pngimage_clang.xml also exists
"""
FILES_TO_RUN = ['libpng/contrib/libtests/pngimage.c/pngimage.c']


""" 
FILES_TO_RUN can contain relative path, set BASE_DIR such that joining BASE_DIR and paths in FILES_TO_RUN using os.path.join
 gives complete path to project code files
"""
BASE_DIR = ""
# Path to a problem domain txt file
PROBLEM_DOMAIN_FILE = "libpng/ProblemDomainConcepts.txt"

# Function to join a given path with BASE_DIR
def PJ(dir):
	return os.path.join(BASE_DIR,dir)

for file in set(FILES_TO_RUN):
	# Setting up variables which contain path to required files
	basename = os.path.basename(file) 		# name of the code file
	file_without_extention = basename.split(".")[0] 
	complete_path_file = PJ(file)
	complete_path_xml = complete_path_file[:-len(basename)]
	complete_path_xml += file_without_extention
	complete_path_xml += "_clang.xml"
	print("Running for file - ",file, complete_path_file, complete_path_xml)

	# Running XML_GetExcelForAFile.py using the code file, clang xml file, problem domain txt file, and program_domain.csv [part of CommentProbe only]
	os.system("python2 XML_GetExcelForAFile.py " + complete_path_file + " Identifier/program_domain.csv "+ PROBLEM_DOMAIN_FILE +" " +complete_path_xml + " " + file)
