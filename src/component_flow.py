import xlrd
import time
import sys

class Component:
	def __init__(self, name, calling=[], called=[]):
		self.name = name
		self.calling = calling
		self.called = called
		self.paths = []
		self.found = False
	def __str__(self):
		return self.name
	
	
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
	components = tuple(graph.keys())
	for componentName in components:
		calling = []
		for name in graph[componentName].calling:
			if name not in graph.keys():
				graph[name] = Component(name=name)
			calling.append(graph[name])
		graph[componentName].calling = calling
		
		
		called = []
		for name in graph[componentName].called:
			if name not in graph.keys():
				graph[name] = Component(name=name)
			called.append(graph[name])
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
		tempPaths = extendPath(path)
		for tempPath in tempPaths:
			if isPathFinished(tempPath,source,target):
				if tempPath[-1] in (source,target):
					if source in tempPath and target in tempPath:
						target.found = False
						relevantPaths.append(tempPath)
						#print("->".join([str(c) for c in path]))
			else:
				#print(" ".join([str(c) for c in tempPath]))
				paths.append(tempPath)
	
	
	return relevantPaths
	
def extendPath(path):
	newPaths = []
	for c in path[-1].called:
		c.paths.append(path + [c])
		if not c.found:
			c.found = True
			newPaths.append(path + [c])
	
	return newPaths
	
	
	
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
	relevantPaths = ["->".join([str(c) for c in path]) for path in relevantPaths]
	return relevantPaths
	
	
if __name__ == "__main__":
	c1 = sys.argv[1]
	c2 = sys.argv[2]
	expandedPaths = main(c1,c2)#"VIB3248","VIB3932")
	for path in expandedPaths:
		print(path)
	
	
	