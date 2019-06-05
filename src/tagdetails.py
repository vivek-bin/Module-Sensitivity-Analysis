import fileaccess as FA
from classes import Component

	
def digestFile(componentName,lib):
	FA.openLib(lib)
	
	file = FA.loadFile(lib,componentName)
	c = Component(componentName,file)
		
	FA.closeLib(lib)
	return c.modificationLog, c.tags

	
def digestFiles(lib,excelFile):
	FA.openLib(lib)
	xli = 0
	fileList = FA.fileListLib(lib)
	for i,fl in enumerate(fileList):
		if not fl.lower().startswith("vifp0"):
			continue
		file = FA.loadFile(lib,fl)
		c = Component(fl,file)
		
	FA.closeLib(lib)
	
def digestFiles(lib,excelFile):
	FA.openLib(lib)
	xli = 0
	fileList = FA.fileListLib(lib)
	for i,fl in enumerate(fileList):
		if not fl.lower().startswith("vifp0"):
			continue
		file = FA.loadFile(lib,fl)
		c = Component(fl,file)
		
		
	FA.closeLib(lib)

def mainFunc():
	digestFiles(FA.COPY,sheet1)


mainFunc()


