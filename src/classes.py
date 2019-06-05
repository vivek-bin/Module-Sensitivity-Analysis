import constants as CONST

class Component:
	def __init__(self,componentName,file):
		self.file = file
		self.componentName = componentName
		self.modificationLog = ""
		self.modificationLogPartitions = []
		self.tags = {}
		self.createdTag = ""
		
		self.modificationLog = self.extractModificationLog()
		self.distributeModLog()
		self.distributeTagLines()
		
		
	def distributeTagLines(self):
		self.initializeTags()
	
		for line in self.file:
			if line[0:1] == chr(26):
				continue
			commented = line[6:7].strip()
			tag1 = line[:6].strip()
			if not tag1:
				tag1 = self.createdTag
			
			if tag1.isnumeric():
				tag1 = self.createdTag
				
			
			
			try:
				self.tags[tag1].extendModifications(line)
			except KeyError:
				self.tags[tag1] = Tag(tag1)
				self.tags[tag1].extendModifications(line)
				#print("tag not found in modification log!  " + self.componentName + " " +tag1)
			
			if commented and tag1 != self.createdTag:
				if line[7:8].strip() == "":
					tag1 = self.createdTag
				else:
					tag2 = line[7:13].strip()
				
				#self.tags[tag2].extendModifications(line)		#DIFFERENTIATE BETWEEN DESCRIPTION COMMENTS AND LINE DELETION COMMENTING
		
		
	def initializeTags(self):
		self.tags[""] = Tag("")
		self.tags[""].extendLog("creation")
		
		tagName = ""
		for line in self.modificationLog:
			if line[:6].strip():
				tagName = line[:6].strip()
			
			tagText = line[7:]
			if tagName not in self.tags:
				self.tags[tagName] = Tag(tagName)
		
			self.tags[tagName].extendLog(tagText)
	
	
	def extractModificationLog(self):
		modificationLog = []
		
		nonCommentCount = 0
		logStarted = False
		for line in self.file:	
			comment = line[6:7].strip()
			if comment != "":
				nonCommentCount = 0
				if line[7:60] in ("*"*53,"="*53,"-"*53):
					logStarted = True
				
				if logStarted:
					modificationLog.append(line)
				continue

			if line[7:72].strip() == "":
				continue
			
			if logStarted:
				break
				
			nonCommentCount += 1
			if nonCommentCount == CONST.LOG_IDENTIFIER_LIMIT:
				break
		
		return modificationLog
		
	
	def distributeModLog(self):
		block = []
		for line in self.modificationLog:
			if line[7:60] in ("*"*53,"="*53,"-"*53):
				if block:
					self.modificationLogPartitions.append(block)
					block = []
			else:
				block.append(line)
		
		
		
class Tag:
	def __init__(self,tagName):
		self.tagName = tagName
		self.tagLines = []
		self.log = ""
		self.numberOfLines = 0
		
		
	def extendLog(self,text):
		self.log = self.log + text + "\n"
		
		
	def extendModifications(self,line):
		self.tagLines.append(line)
		self.numberOfLines += 1
		
		
		