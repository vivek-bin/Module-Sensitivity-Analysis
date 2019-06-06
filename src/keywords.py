import constants as CONST
import fileaccess
allKeyWords = []
mainVerbs = []

def extractKeywords(inputLine):
	if inputLine[-1] == ".":
		inputLine = inputLine[:-1]
	words = inputLine.split()
	keyWords = [w for w in words if w in allKeyWords]
	return keyWords
	
def extractNonKeywords(inputLine):
	if inputLine[-1] == ".":
		inputLine = inputLine[:-1]
	words = inputLine.split()
	nonKeyWords = [w for w in words if w not in allKeyWords]
	return nonKeyWords
	
def isKeyword(word):
	if word in allKeyWords:
		return True
	else:
		return False
		
def isMainVerb(word):
	if word in mainVerbs:
		return True
	else:
		return False

allKeyWords = fileaccess.loadDATA("Keywords")
mainVerbs = fileaccess.loadDATA("MainKeywords")
