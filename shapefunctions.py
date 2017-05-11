from plotfunctions import *
import fiona

def test (inFile, variable, sites, sitetypes, plotmode=0):
    dataList = getdata(inFile, variable, sites, sitetypes, plotmode)
    return dataList
