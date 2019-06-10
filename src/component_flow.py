import xlrd
import time

class Component:
	def __init__(self, name, calling, called):
		self.name = name
		self.calling = calling
		self.called = called


def readExcel():
	wb = xlrd.open_workbook("vifp0 details.xls") 
	sheet = wb.sheet_by_index(0) 
	 
	graph = {}
	for i in range(1,sheet.nrows):
		name = sheet.cell_value(i, 4).strip()
		if name:
			calling = sheet.cell_value(i, 6).strip()
			called = sheet.cell_value(i, 7).strip()
			calling = calling.replace("\n"," ").split()
			called = called.replace("\n"," ").split()
			
			graph[name] = Component(name=name,calling=calling,called=called)
		
	modules = set()
	for componentName in graph.keys():
		calling = [c for c in graph[componentName].calling if c in graph.keys()]
		calling = [graph[name] for name in calling]
		
		called = [c for c in graph[componentName].called if c in graph.keys()]
		called = [graph[name] for name in called]
		
		graph[componentName].calling = calling
		graph[componentName].called = called
	
	
	return graph
	

def findPaths(source,target):	
	graph = readExcel()
	source = graph[source]
	target = graph[target]
	relevantPaths = []
	
	paths = [[source]]
	while(paths):
		path = paths.pop(0)
		tempPaths = [path+[c] for c in path[-1].called]
		print(len(paths))
		for tempPath in tempPaths:
			if isPathFinished(tempPath,source,target):
				if tempPath[-1] in (source,target):
					if source in tempPath and target in tempPath:
						relevantPaths.append(tempPath)
						#print("->".join([c.name for c in path]))
			else:
				#print(" ".join([c.name for c in tempPath]))
				paths.append(tempPath)
	
	
	return relevantPaths
	
	
def isPathFinished(path,source,target):
	lastC = path[-1]
	
	if not lastC.called:
		return True
	if lastC in (source,target):
		return True
	if lastC in path[:-1]:
		return True
	
	
	return False
	
	
def main(prog1,prog2):
	relevantPaths = findPaths(prog1,prog2) + findPaths(prog2,prog1)
	relevantPaths = ["->".join([c.name for c in path]) for path in relevantPaths]
	return relevantPaths
	
expandedPaths = main("VIC3I13","VIC3B88")
for path in expandedPaths:
	print(path)
	
	
	