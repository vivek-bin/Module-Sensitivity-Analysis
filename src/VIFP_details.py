import fileaccess as FA
from classes import Component

import xlwt 
from xlwt import Workbook 


def processFiles(excelFile):
	FA.openLib(FA.COPY)
	fileList = FA.fileListLib(FA.COPY)
	FA.closeLib(FA.COPY)
	fileList = [f for f in fileList if f.startswith("VIFP0K02")]
	
	
	xli = 0
	for i,fl in enumerate(fileList):
		FA.openLib(FA.COPY)
		file = FA.loadFile(FA.COPY,fl)
		FA.closeLib(FA.COPY)
		
		c = Component(fl,file)
		print("loaded "+fl)
		
		for logText in c.modificationLogPartitions:
			if len(logText) > 1:
				d = digestModLog(logText)
				break
		
		
		try:
			serviceName = findServiceNameVIFP(file)
		except:
			print(fl)
			raise Exception
		serviceCallingPrograms = searchLib(FA.EXPANDED,"PERFORM "+serviceName+"-",componentFilter="VI",searchStart=11)
		
		programs = searchLib(FA.SRCE,fl,componentFilter="VI",searchStart=7)
		programCallingCopy = {}
		callingPrograms = {}
		calledPrograms = {}
		for program in programs:
			programCallingCopy[program] = searchLib(FA.COPY,program,componentFilter="VIFP",searchStart=7)
			
			cP = searchLib(FA.EXPANDED,program,componentFilter="VI",searchStart=7)
			callingPrograms[program] = [p for p in serviceCallingPrograms if p in cP]
			calledPrograms[program] = findCalledServices(program)
			if program in calledPrograms[program]:
				calledPrograms[program].remove(program)
		
		excelFile.write(xli,0,fl)
		excelFile.write(xli,1,"\n".join(d["REMARKS"]))
		excelFile.write(xli,2,"\n".join(d["DOMAIN"]))
		excelFile.write(xli,3,"\n".join(d["CLASS"]))
		for j,program in enumerate(programs):
			excelFile.write(xli,4,program)
			excelFile.write(xli,5,"\n".join(callingPrograms[program]))
			excelFile.write(xli,6,"\n".join(calledPrograms[program]))
			
			if j < len(programs) - 1:
				xli += 1
		
		
		xli += 1
		


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
	
	FA.openLib(lib)
	fileList = FA.fileListLib(lib)
	fileList = [f for f in fileList if f.startswith(componentFilter)]
	for i,fl in enumerate(fileList):
		file = FA.loadFile(lib,fl)
		for line in file:
			if skipCommented and line[6:7] in ("*","/","\\"):
				continue
				
			line = line[searchStart:searchEnd+1]
			
			if concatSpaces:
				line = " ".join(line.split())
			
			if text in line:
				componentList.append(fl)
				break
		
	FA.closeLib(lib)
	
	return componentList


def findServiceNameVIFP(file):
	for line in file:
		if line[6:7] in ("*","/","\\"):
			continue
			
		if line[7:11].strip():
			return line[7:11]
			
	raise Exception


def findServiceNameVIFW(file):
	for line in file:
		if line[6:7] in ("*","/","\\"):
			continue
		
		if line[7:].strip():
			words = line[7:].split()
			if words[0].isnumeric():
				return words[1][1:5]
			
	raise Exception

	
def findCalledServices(fileName):
	FA.openLib(FA.SRCE)
	file = FA.loadFile(FA.SRCE,fileName)
	FA.closeLib(FA.SRCE)
	
	FWList = []
	for line in file:
		if line[6:7] in ("*","/","\\"):
			continue
		
		words = line[7:72].replace("."," . ").split()
		
		if words and words[0] == "COPY":
			if words[1].startswith("VIFW"):
				FWList.append(words[1])
	
	
	servicesList = []	
	FA.openLib(FA.COPY)
	for f in FWList:
		copyFile = FA.loadFile(FA.COPY,f)
		servicesList.append(findServiceNameVIFW(copyFile))
	FA.closeLib(FA.COPY)
	
	FA.openLib(FA.EXPANDED)
	file = FA.loadFile(FA.EXPANDED,fileName)
	FA.closeLib(FA.EXPANDED)
	
	programs = []
	for serviceTag in servicesList:
		flag = False
		for line in file:
			if line[6:7] in ("*","/","\\"):
				continue
			
			line = " ".join(line[7:72].split())
			if "PERFORM "+serviceTag+"-" in line:
				flag = True
				break
		if not flag:
			continue
		
		
		serviceCopyList = searchLib(FA.COPY,serviceTag,componentFilter="VIFP0",searchStart=7,searchEnd=12)
		serviceProgramList = []
		for service in serviceCopyList:
			serviceProgramList.extend(searchLib(FA.SRCE,service,componentFilter="VI",searchStart=7))
			
		for program in serviceProgramList:
			for line in file:
				if line[6:7] in ("*","/","\\"):
					continue
				
				line = line[7:72]
				if program in line:
					programs.append(program)
					break
	
	return programs

	
	
	
	
def mainFunc():
	# Workbook is created 
	wb = Workbook() 
	# add_sheet is used to create sheet. 
	sheet1 = wb.add_sheet('Sheet 1') 

	processFiles(sheet1)


	wb.save('vifp0 details.xls') 


mainFunc()

