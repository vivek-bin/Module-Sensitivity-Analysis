import fileaccess as FA
from classes import Component


	
def digestFile(componentName,lib):
	FA.openLib(lib)
	
	file = FA.loadFile(lib,componentName)
	c = Component(componentName,file)
		
	FA.closeLib(lib)
	return c.modificationLog, c.tags

	
def digestFiles(lib):
	FA.openLib(lib)
	
	fileList = FA.fileListLib(lib)
	for fl in fileList:
		if fl[2:4].lower() == "ms":
			continue
		file = FA.loadFile(lib,fl)
		c = Component(fl,file)
		
	FA.closeLib(lib)
	#return c.modificationLog, c.tags

	
	
#modLog,tagDict = digestFile("VIC3103",FA.SRCE)

digestFiles(FA.COPY)

#for line in modLog:
#	print(line)

