import fileaccess as FA
from classes import Component

import time
import threading
from xlwt import Workbook 

FILE_LEN_MIN = 30
FILE_LEN_MAX = 9999999
FIND_CALLING = True
FIND_CALLED = True
THREADS = 1

FA.openLib(FA.COPY)
fileList = FA.fileListLib(FA.COPY)
fileList = [f for f in fileList if f.startswith("VIF")]
COPYLIB = {}
for fl in fileList:
	COPYLIB[fl] = FA.loadFile(FA.COPY,fl)
FA.closeLib(FA.COPY)


FA.openLib(FA.SRCE)
fileList = FA.fileListLib(FA.SRCE)
fileList = [f for f in fileList if f.startswith("VI")]
SRCELIB = {}
for fl in fileList:
	SRCELIB[fl] = FA.loadFile(FA.SRCE,fl)
FA.closeLib(FA.SRCE)


FA.openLib(FA.EXPANDED)
fileList = FA.fileListLib(FA.EXPANDED)
fileList = [f for f in fileList if f.startswith("VI")]
EXPANDED = {}
for fl in fileList:
	EXPANDED[fl] = FA.loadFile(FA.EXPANDED,fl)
FA.closeLib(FA.EXPANDED)


def processFiles(fileList,excelName,lock):
	processedDict = {}
	startTime = time.time()
	
	for fileName in fileList:
		processFile(fileName,processedDict)
	
	with lock:
		writeExcel(processedDict,excelName)
	
	
	print(str(time.time() - startTime))
	return processedDict


def processFile(fileName,processedDict):
	global COPYLIB,SRCELIB,EXPANDED
	global FILE_LEN_MIN,FILE_LEN_MAX,FIND_CALLING,FIND_CALLED
	
	file = COPYLIB[fileName]
	
	if len(file)<FILE_LEN_MIN or len(file)>FILE_LEN_MAX:
		print("unusual VIFP")
		return False
	
	c = Component(fileName,file)
	print("loaded "+c.componentName)
	
	for logText in c.modificationLogPartitions:
		if len(logText) > 1:
			c.details = digestModLog(logText)
			break
	
	c.serviceName = findServiceNameVIFP(c.file)
	c.programs = searchLib(SRCELIB,c.componentName,componentFilter="VI",searchStart=7)
	
	c.programCallingCopy = {}
	c.callingPrograms = {}
	c.calledPrograms = {}
	for program in c.programs:
		c.programCallingCopy[program] = []
		c.callingPrograms[program] = []
		c.calledPrograms[program] = []
	
	
	if FIND_CALLING:
		if c.serviceName:
			serviceCallingPrograms = searchLib(EXPANDED,"PERFORM "+c.serviceName+"-",componentFilter="VI",searchStart=11)
		else:
			serviceCallingPrograms = EXPANDED.keys()
		
	for program in c.programs:
		c.programCallingCopy[program] = searchLib(COPYLIB,program,componentFilter="VIFP",searchStart=7)
		
		if FIND_CALLING:
			#instead of searching entire EXPANDED, search just relevant components
			for serviceProgram in serviceCallingPrograms:
				file = EXPANDED[serviceProgram]
				for line in file:
					if line[6:7].strip():
						continue
					if program in line:
						c.callingPrograms[program].append(serviceProgram)
						break
			if program in c.callingPrograms[program]:
				c.callingPrograms[program].remove(program)
		
		if FIND_CALLED:	
			c.calledPrograms[program] = findCalledServices(program)
			if program in c.calledPrograms[program]:
				c.calledPrograms[program].remove(program)
		
	processedDict[fileName] = c
	
	return c

	
def writeExcel(processedDict,name):
	# Workbook is created 
	wb = Workbook() 
	# add_sheet is used to create sheet. 
	excelFile = wb.add_sheet('Sheet 1') 
	
	xli = 0
	for fileName in sorted(processedDict.keys()):
		c = processedDict[fileName]
		excelFile.write(xli,0,c.componentName)
		excelFile.write(xli,1,"\n".join(c.details["REMARKS"]))
		excelFile.write(xli,2,"\n".join(c.details["DOMAIN"]))
		excelFile.write(xli,3,"\n".join(c.details["CLASS"]))
		for j,program in enumerate(c.programs):
			if j:
				excelFile.write(xli,0,c.componentName)
				excelFile.write(xli,1,"\n".join(c.details["REMARKS"]))
				excelFile.write(xli,2,"\n".join(c.details["DOMAIN"]))
				excelFile.write(xli,3,"\n".join(c.details["CLASS"]))
			excelFile.write(xli,4,program)
			excelFile.write(xli,5,"\n".join(c.programCallingCopy[program]))
			excelFile.write(xli,6,"\n".join(c.callingPrograms[program]))
			excelFile.write(xli,7,"\n".join(c.calledPrograms[program]))
			
			if j < len(c.programs) - 1:
				xli += 1
		
		xli += 1
		
	
	wb.save(name) 


def digestModLog(text):
	description = []
	for l in text:
		l = l[7:]
		while l[0:1] == "*":
			l = l[1:]
		while l[-1:] == "*":
			l = l[:-1]
		description.append(l.strip())
	
	desc2 = []
	while True:
		if description[0].startswith("MEMBER"):
			break
		else:
			description = description[1:]
			if not description:
				break
				
	label = ""
	logDict = {}
	logDict["MEMBER"] = []
	logDict["REMARKS"] = []
	logDict["DOMAIN"] = []
	logDict["CLASS"] = []
	logDict["ATTENTION"] = []
	keyList = logDict.keys()
	for l in description:
		if l.strip():
			for k in keyList:
				if l.startswith(k):
					label = k
					l = l[max(len(k)+2,9):].strip()
					logDict[label].append("")
					break
			
			logDict[label][-1] = logDict[label][-1] + l + " "
		else:
			if not logDict[label][-1]:
				logDict[label].append("")
	
	for key in logDict.keys():
		logDict[key] = [l.strip() for l in logDict[key]]
	return logDict
	
	
def searchLib(lib,text,componentFilter="",skipCommented=True,concatSpaces=True,searchStart=0,searchEnd=999):
	componentList = []
	
	fileList = lib.keys()
	fileList = [f for f in fileList if f.startswith(componentFilter)]
	for fl in fileList:
		file = lib[fl]
		if skipCommented:
			file = [line[searchStart:searchEnd+1] for line in file if not line[6:7].strip()]
		
		if concatSpaces:
			file = [" ".join(line.split()) for line in file]
		
		for line in file:
			if text in line:
				componentList.append(fl)
				break
		
	
	return componentList


def findServiceNameVIFP(file):
	if len(file)<30:
		return ""
	
	for line in file:
		if line[6:7].strip():
			continue
			
		if line[7:11].strip():
			return line[7:11]
	
	raise Exception


def findServiceNameVIFW(file):
	for line in file:
		if line[6:7].strip():
			continue
		
		words = line[7:].split()
		if words and words[0].isnumeric():
				return words[1][1:5]
			
	raise Exception

	
def findCalledServices(fileName):
	global COPYLIB,SRCELIB,EXPANDED
	
	file = SRCELIB[fileName]
	
	FWList = []
	for line in file:
		if line[6:7].strip():
			continue
		
		words = line[7:72].replace("."," . ").split()
		
		if words and words[0] == "COPY":
			if words[1].startswith("VIFW"):
				FWList.append(words[1])
	
	
	servicesList = []	
	for f in FWList:
		copyFile = COPYLIB[f]
		servicesList.append(findServiceNameVIFW(copyFile))
	
	file = EXPANDED[fileName]
	
	programs = []
	for serviceTag in servicesList:
		flag = False
		for line in file:
			if line[6:7].strip():
				continue
			
			line = " ".join(line[7:72].split())
			if "PERFORM "+serviceTag+"-" in line:
				flag = True
				break
		if not flag:
			continue
		print(serviceTag)
		
		serviceCopyList = searchLib(COPYLIB,serviceTag,componentFilter="VIFP0",searchStart=7,searchEnd=12)
		serviceProgramList = []
		for service in serviceCopyList:
			serviceProgramList.extend(searchLib(SRCELIB,service,componentFilter="VI",searchStart=7))
			
		for program in serviceProgramList:
			for line in file:
				if line[6:7].strip():
					continue
				
				line = line[7:72]
				if program in line:
					programs.append(program)
					break
	
	return programs



	
def mainFunc():
	global COPYLIB,THREADS
	
	fileList = COPYLIB.keys()
	fileList = [f for f in fileList if f.startswith("VIFP0N06")]
	threadList = []
	
	lock = threading.Lock()
	
	for i in range(THREADS):
		temp = [f for j,f in enumerate(fileList) if j%THREADS == i]
		newThread = threading.Thread(target=processFiles, args=(temp,"vifp0 details"+str(i)+".xls",lock))
		newThread.start()
		threadList.append(newThread)
		

mainFunc()

