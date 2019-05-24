from inspect import getsourcefile
from os.path import abspath
from os.path import dirname

#paths
PATH = dirname(dirname(dirname(abspath(getsourcefile(lambda:0))))) + "/"

MTP = PATH + "MTP/"
MTPZIP = PATH + "MTP ZIP/"
PROJECT = PATH + "PROJECT/"

SRCELIB = MTP + "SRCELIB/"
COPYLIB = MTP + "COPYLIB/"
INCLUDE = MTP + "INCLUDE/"
EXPANDED = MTP + "EXPANDED/"
PROCESSING = MTP + "PROCESSING/"
TREES = MTP + "TREES/"

SRCEZIP = MTPZIP + "SRCELIB.zip"
COPYZIP = MTPZIP + "COPYLIB.zip"
INCZIP = MTPZIP + "INCLUDE.zip"
EXPANDEDZIP = MTPZIP + "EXPANDED.zip"
PROCESSINGZIP = MTPZIP + "PROCESSING.zip"
TREESZIP = MTPZIP + "TREES.zip"


LOG_IDENTIFIER_LIMIT = 4
