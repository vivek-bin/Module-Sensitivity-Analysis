import zipfile
import constants as CONST
import pickle
import os
from nodes import *

SRCE = 0
COPY = 1
INC = 2
EXPANDED = 3
TREES = 4

ZIPPATHS = {}
ZIPPATHS[SRCE] = CONST.SRCEZIP
ZIPPATHS[COPY] = CONST.COPYZIP
ZIPPATHS[INC] = CONST.INCZIP
ZIPPATHS[EXPANDED] = CONST.EXPANDEDZIP
ZIPPATHS[TREES] = CONST.TREESZIP

FILENAMEPREFIX = {}
FILENAMEPREFIX[SRCE] = CONST.COBOLLIB + ".SRCELIB."
FILENAMEPREFIX[COPY] = CONST.COBOLLIB + ".COPYLIB."
FILENAMEPREFIX[INC] = CONST.COBOLLIB + ".INCLUDE."
FILENAMEPREFIX[EXPANDED] = CONST.COBOLLIB + ".EXPANDED."
FILENAMEPREFIX[TREES] = CONST.COBOLLIB + ".TREES."

zips = {}

def openLib(lib,mode="r"):
	if lib not in zips.keys():
		if mode in ["w","a"]:
			zips[lib] = zipfile.ZipFile(ZIPPATHS[lib],mode,zipfile.ZIP_DEFLATED)
		else:
			zips[lib] = zipfile.ZipFile(ZIPPATHS[lib],mode)
	else:
		print("library already open")
	
def fileListLib(lib):
	fileList = zips[lib].namelist()
	fileList = [fileName[len(FILENAMEPREFIX[lib]):] for fileName in fileList]
	return fileList
	
def validComponentName(component):
	component = FILENAMEPREFIX[EXPANDED] + component.upper()
	
	e = zipfile.ZipFile(CONST.EXPANDEDZIP)
	exists = component  in e.namelist()
	e.close()
	
	return exists
	
def extractExpandedFile(fileName):
	fileName = FILENAMEPREFIX[EXPANDED] + fileName.upper()
	if not os.path.isfile(CONST.EXPANDED + fileName):
		zips[EXPANDED] = zipfile.ZipFile(ZIPPATHS[EXPANDED])
		zips[EXPANDED].extract(fileName, CONST.EXPANDED)
		zips[EXPANDED].close()
	return CONST.EXPANDED + fileName
	
def loadFile(lib,fileName):
	try:
		f = zips[lib].read(FILENAMEPREFIX[lib]+fileName.upper())
		f = f.decode("cp852")
		
		f = f.split("\r\n")
	except KeyError:
		f = []
		
	if lib in (SRCE,COPY,INC):
		f = [l[:72].rstrip() for l in f]
	else:
		f = [l.rstrip() for l in f]
	return f
	
def writeFile(lib,fileName,file):
	zips[lib].writestr(FILENAMEPREFIX[lib]+fileName,"\r\n".join(file))

def closeLib(lib):
	zips[lib].close()
	del zips[lib]

	
	
def loadDATA(inputFileName):
	f = []
	try:
		iFile = open(CONST.DATA+inputFileName+".txt")

		f = [l.rstrip() for l in iFile]
		iFile.close()
	except IOError:
		f = []
	return f
	
def appendDATA(inputFileName,inputLine):
	try:
		iFile = open(CONST.DATA+inputFileName+".txt","a")

		iFile.write(inputLine+"\n")
		iFile.close()
		return False
	except IOError:
		print("Append IO error")
		return False

def writeDATA(inputFileName,inputLine=""):
	try:
		iFile = open(CONST.DATA+inputFileName+".txt","w")

		iFile.write(inputLine+"\n")
		iFile.close()
		return False
	except IOError:
		return False

def writeLOG(inputLine):
	appendDATA("log",inputLine)



def writePickle(outputFileName,file):
	outputFile = open(CONST.TREES+FILENAMEPREFIX[TREES]+outputFileName,"wb")
	pickle.dump(file,outputFile)
	outputFile.close()
	
def loadPickle(outputFileName):
	outputFile = open(CONST.TREES+FILENAMEPREFIX[TREES]+outputFileName,"rb")
	file = pickle.load(outputFile)
	outputFile.close()
	return file




