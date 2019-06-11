import constants as CONST
import keywords
import fileaccess
import os
import time

def expandFile(inputFile):
	file = []
	
	lineNo = -1
	while lineNo < len(inputFile) - 1:
		lineNo += 1
		inputLine = inputFile[lineNo]
		if len(inputLine) < 8:
			file.append(inputLine)
			continue
		if inputLine[6] != " ":
			file.append(inputLine)
			continue
		
		inputLineStrip = inputLine[7:].lower()
		inputLineStrip = " ".join(inputLineStrip.split())
		if inputLineStrip[:5] == "copy " or inputLineStrip[:8] == "exec sql":
			specialBlock = []
			specialBlock.append(inputLine)
			while inputLine[6] != " " or ("." not in inputLine and "end-exec" not in inputLine.lower()):
				lineNo += 1
				inputLine = inputFile[lineNo]
				if len(inputLine) < 8:
					inputLine += "        "
				specialBlock.append(inputLine)
			
			inputLine = ""
			for specialLine in specialBlock:
				if specialLine[6] == " ":
					inputLine += specialLine[7:]
			inputLine = " ".join(inputLine.split()).lower().replace("."," ")
			
			expandFlag = True
			if inputLine[:5] == "copy ":
				copyFileName = inputLine[5:inputLine.find(" ",5)]
			elif inputLine[:17] == "exec sql include ":
				copyFileName = inputLine[17:inputLine.find(" ",17)]
			else:
				expandFlag = False
			
			for specialLine in specialBlock:
				if specialLine[6] == " " and expandFlag:
					specialLine = specialLine[:6] + "*" + specialLine[7:]
				file.append(specialLine)
				
			if expandFlag:
				copyFile = fileaccess.loadFile(fileaccess.COPY,copyFileName)
				if not copyFile:
					copyFile = fileaccess.loadFile(fileaccess.INC,copyFileName)
				
				if "replacing" in inputLine:
					inputLine = inputLine[inputLine.find("replacing") + len("replacing") + 1:-1].strip()
					inputLine = inputLine.replace("==","").replace("'","").strip()
					replacedText = inputLine[:inputLine.find(" ")].upper()
					replacingText = inputLine[inputLine.rfind(" ") + 1:].upper()
					
					copyFile = [l.replace(replacedText, replacingText) for l in copyFile]
				file.extend(copyFile)
			continue
		
		file.append(inputLine)
	
	return file

def processingFile(inputFile):
	file = []
	
	for i, inputLine in enumerate(inputFile):
		inputLine = inputLine.lower().rstrip()
		if len(inputLine) < 8:
			continue
		if inputLine[6] == "-":
			for i in range(7,len(inputLine)):
				if inputLine[i] != " ":
					break
			inputLine = inputLine[:6] + " " + inputLine[7:i]+chr(255)+inputLine[i+1:]
		if inputLine[6] != " ":
			continue
		if inputLine.replace(".","").strip() == "eject":
			continue
		if " title " in inputLine:
			continue
			
		inputLine = inputLine[7:]

		if inputLine[:4] == "    ":
			inputLine = " ".join(inputLine.split())
			inputLine = inputLine.replace("( ","(").replace(" )",")")
			inputLine = inputLine.replace("("," (").replace(")",") ")
			words = inputLine.split()
			
			inputLine = prevWord = words[0]
			for currWord in words[1:]:
				if currWord[0] != "(" or keywords.isKeyword(prevWord):
					inputLine += " "
				inputLine += currWord
				prevWord = currWord
					
			#inputLine = inputLine.replace(" (","(")
			inputLine = "    " + inputLine
		else:
			inputLine = " ".join(inputLine.split())
		file.append(str(i).zfill(CONST.ZEROPAD) + inputLine)
		
	return file

def processingFileClean(inputFile):
	file = []
	inputProcedureDivision = []
	inputDataDivision = []

	for i,inputLine in enumerate(inputFile):
		if inputLine[CONST.ZEROPAD:].startswith("procedure division"):		#line count CONST.ZEROPAD digits
			inputProcedureDivision = inputFile[i:]
			inputFile = inputFile[:i]
			break
			
	for i,inputLine in enumerate(inputFile):
		if inputLine[CONST.ZEROPAD:].startswith("data division"):		#line count CONST.ZEROPAD digits
			inputDataDivision = inputFile[i:]
			inputFile = inputFile[:i]
			break
	
	file = inputFile
	
	line = ""
	for inputLine in inputDataDivision:
		if line:
			line += " " + inputLine[CONST.ZEROPAD:].strip()
		else:
			line = inputLine
			
		if inputLine[-1] == ".":
			file.append(line)
			line = ""

	line = ""
	execFlag = False
	for i,inputLine in enumerate(inputProcedureDivision):
		lineNo = inputLine[:CONST.ZEROPAD]
		inputLine = inputLine[CONST.ZEROPAD:]
		
		inputWords = inputLine.replace(".","").split()
		
		if not inputWords:
			if line:
				file.append(line)
				line = ""
			file.append(lineNo + inputLine)
			continue
		
		if inputWords[0] in ["id","identification"] and inputWords[1] == "division":
			if line:
				file.append(line)
				line = ""
			file.extend(processingFileClean(inputProcedureDivision[i:]))
			break
		
		if inputWords[0] == "procedure" and inputWords[1] == "division":
			if line:
				file.append(line)
			line = lineNo + inputLine
			continue
			
		if inputLine[0] != " " and len(inputWords) == 2 and inputWords[1] == "section":
			if line:
				file.append(line)
				line = ""
			file.append(lineNo + inputWords[0]+".")
			continue
			
		if inputLine[0] != " ":
			if line:
				file.append(line)
				line = ""
			if inputWords[0] == "end" and inputWords[1] == "program":
				file.append(lineNo + inputLine)
			else:
				file.append(lineNo + inputWords[0]+".")
			continue			
		
		if inputWords[0] == "exec":
			execFlag = True
			if line:
				file.append(line)
				line = ""
		if "end-exec" in inputWords:
			file.append(lineNo + inputLine)
			execFlag = False
			continue
		if execFlag:
			file.append(lineNo + inputLine)
			continue
			
		if  keywords.isMainVerb(inputWords[0]) or inputLine[0] != " ":
			if line:
				file.append(line)
			line = lineNo + inputLine
		else:
			if line:
				line = line + " " + inputLine.strip()
			else:
				line = lineNo + inputLine
	if line:
		file.append(line)
	
	return file

def processingFileCleanData(inputFile):
	file = []
	line = ""
	for inputLine in inputFile:
		if line:
			line += " " + inputLine[CONST.ZEROPAD:].strip()
		else:
			line = inputLine
			
		if inputLine[-1] == ".":
			file.append(line)
			line = ""

	if line:
		file.append(line)
	
	return file

def isCobolProgram(inputFile):
	for inputLine in inputFile:
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		
		inputLine = " ".join(inputLine[6:].split()).lower()
				
		if inputLine == "eject" or inputLine == "eject.":
			continue
			
		if "identification " in inputLine or "id " in inputLine:
			if " division" in inputLine:
				return True
		
		if inputLine[:5] == "copy ":
			if inputLine[5:13].replace(".","").strip() in ["igacces","pcr33010","pcr33019","tccp002"]:
				return True
		
		return False
	return False

def writeProcessingExpand(componentName):
	src = fileaccess.loadFile(fileaccess.SRCE,componentName)
	if not isCobolProgram(src):
		if componentName[2:4].lower() != "ms":
			print("not COBOL:" + componentName)
		fileaccess.writeFile(fileaccess.EXPANDED,componentName,src)
	else:
		expandedSrc = expandFile(src)
		fileaccess.writeFile(fileaccess.EXPANDED,componentName,expandedSrc)
	
def getIncludedCopybooks(inputFile):
	file = []
	
	lineNo = -1
	while lineNo < len(inputFile) - 1:
		lineNo += 1
		inputLine = inputFile[lineNo]
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		
		inputLineStrip = inputLine[7:].lower()
		inputLineStrip = " ".join(inputLineStrip.split())
		if inputLineStrip[:5] == "copy " or inputLineStrip[:8] == "exec sql":
			specialBlock = []
			specialBlock.append(inputLine)
			while lineNo < len(inputFile)-1 and (inputLine[6] != " " or ("." not in inputLine and "end-exec" not in inputLine.lower())):
				lineNo += 1
				inputLine = inputFile[lineNo]
				if len(inputLine) < 8:
					inputLine += "        "
			
			inputLine = ""
			for specialLine in specialBlock:
				if specialLine[6] == " ":
					inputLine += specialLine[7:]
			inputLine = " ".join(inputLine.split()).lower().replace("."," ")
			
			expandFlag = True
			if inputLine[:5] == "copy ":
				copyFileName = inputLine[5:inputLine.find(" ",5)]
			elif inputLine[:17] == "exec sql include ":
				copyFileName = inputLine[17:inputLine.find(" ",17)]
			else:
				expandFlag = False
				
			if expandFlag:
				file.append(copyFileName)
			continue
		
	return file
	
def writeAllProcessingExpand(start=0,end=999999):
	startTime = time.time()
	
	fileaccess.openLib(fileaccess.SRCE)
	fileaccess.openLib(fileaccess.COPY)
	fileaccess.openLib(fileaccess.INC)
	fileaccess.openLib(fileaccess.EXPANDED,"w")
	
	l = fileaccess.fileListLib(fileaccess.SRCE)
	processingList = l[start:end]
	
	for fileName in processingList:
		writeProcessingExpand(fileName)
		
	fileaccess.closeLib(fileaccess.SRCE)
	fileaccess.closeLib(fileaccess.COPY)
	fileaccess.closeLib(fileaccess.INC)
	fileaccess.closeLib(fileaccess.EXPANDED)

		
	print(time.time() - startTime)
	
	

if __name__ == "__main__":
	writeAllProcessingExpand()

