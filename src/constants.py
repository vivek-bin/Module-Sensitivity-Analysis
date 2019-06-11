from inspect import getsourcefile
from os.path import abspath
from os.path import dirname

#paths
PATH = dirname(dirname(dirname(abspath(getsourcefile(lambda:0))))) + "/"
PROJECT = dirname(dirname(abspath(getsourcefile(lambda:0)))) + "/"

COBOLLIB = "MTP.CCCV000"
COBOLLIBHEAD = COBOLLIB[:3]

COBOLLIBPATH = PATH + COBOLLIBHEAD + "/"
ZIPLIBPATH = PATH + COBOLLIBHEAD + " ZIP/"

SRCELIB = COBOLLIBPATH + "SRCELIB/"
COPYLIB = COBOLLIBPATH + "COPYLIB/"
INCLUDE = COBOLLIBPATH + "INCLUDE/"
EXPANDED = COBOLLIBPATH + "EXPANDED/"
TREES = COBOLLIBPATH + "TREES/"

SRCEZIP = ZIPLIBPATH + "SRCELIB.zip"
COPYZIP = ZIPLIBPATH + "COPYLIB.zip"
INCZIP = ZIPLIBPATH + "INCLUDE.zip"
EXPANDEDZIP = ZIPLIBPATH + "EXPANDED.zip"
TREESZIP = ZIPLIBPATH + "TREES.zip"

DATA = PROJECT + "data/"

#line number tracking
ZEROPAD = 8


#flowchart values
TOOLTIPSIZE = 50

NPLOCATION = "C:\\Program Files\\Notepad++\\notepad++.exe"

BRANCHSPACE = 30

FONT = ("League Gothic",9,"bold")
TOOLTIPFONT = ("Times New Roman",7,"normal")

ICONS = PROJECT + "icons/"


FLOWCUSTOM = DATA + "flowchart-customize/"
def loadCustomization(inputFileName):
	f = []
	try:
		iFile = open(FLOWCUSTOM+inputFileName+".txt")

		f = [l.strip().lower() for l in iFile]
		iFile.close()
	except IOError:
		f = []
	return f

IGNOREDMODULES = loadCustomization("ignore-program")
IGNOREDPARAS = loadCustomization("ignore-para")

