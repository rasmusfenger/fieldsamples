import os
import sys
import pandas as pd
import numpy as np
from dictionaries import *

class Data(object):
    def __init__(self, site, sitetype, plot, observation, depth=None):
        self.site = site
        self.sitetype = sitetype
        self.observation = observation
        self.plot = plot
        self.depth = depth

class Variable(object):
    # Defines a variable class based on info in csv file in root.
    def __init__(self, variable):
        inFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'variable_data.csv')
        df = np.loadtxt(inFile, delimiter=',', skiprows=1, dtype=str)
        for row in df:
            if int(row[0]) == int(variable):
                self.var = int(row[0])
                self.title = row[1]
                self.sheet = row[2]
                self.column = int(row[3])
                self.xname = row[4]
                self.yname = row[5]
                self.isdepth = row[6]
                self.log = False
                if str(variable - int(variable)) == '0.1':
                    self.log = True
                    self.xname += '- log'

def check_input(inFile, site, stype, variable_1, variable_2, plotmode, savefig):
    def print_error(errList):
        # Error messages
        errMes = {1: 'inFile does not exist',
                  2: 'sites not valid',
                  3: 'site type not valid',
                  4: 'plotmode not valid',
                  5: 'variable_1 not valid',
                  6: 'variable_2 not valid',
                  7: 'selected variable_1 cannot be combined with plotmode 1 or 2',
                  8: 'selected variable_1 or variable_2 cannot be combined with plotmode 4',
                  9: 'path for saving figure does not exist'}
        print 'Error - Wrong input!'
        for err in errList:
            print errMes[err]
        sys.exit(0)

    # Valid parameters
    siteValid = [1,2,3,4,5,6,7]
    stypeValid = [1,2,3]
    variableValid = [1,2,3,4,5,6,7,8,10,11,12,13,14,15,20,21,22,30,31,32,33,34,35,36,40,41,42,43,44,45,46,47,48,49]
    plotmodeValid = ['1', '2', '2.1', '2.2', '2.3', '3', '4', '4.1', '4.2', '4.3']
    errList = []
    # First check input parameters
    if not os.path.isfile(inFile):
        errList.append(1)
    if not site in siteValid:
        errList.append(2)
    if not stype in stypeValid:
        errList.append(3)
    if not int(variable_1) in variableValid:
        errList.append(5)
    if not str(plotmode) in plotmodeValid:
        errList.append(4)
    if savefig:
        if not os.path.isdir(savefig):
            errList.append(9)
    if errList:
        print_error(errList)
    # Then check combination of input parameters
    else:
        var1 = Variable(variable_1)
        if int(plotmode) == 1 or int(plotmode) == 2:
            #variable_1 has to have depth observations
            if var1.isdepth == 'no':
                errList.append(7)
        elif int(plotmode) == 3:
            if not int(variable_2) in variableValid:
                errList.append(6)
        elif int(plotmode) == 4:
            if not int(variable_2) in variableValid:
                errList.append(6)
            else:
                # variable_1 and variable_2 cannot have depth observations
                var2 = Variable(variable_2)
                if var1.isdepth == 'yes' or var2.isdepth == 'yes':
                    errList.append(8)
        if errList:
            print_error(errList)

def data_transform(observation, variable):
    # Use this function to modify the data.
    # For only used for log transformation, but more can be added by modifying
    # this function and the Variable class.
    if variable.log:
        # log transform
        obsModified = np.log10(np.asarray(observation) + 1)
    else:
        obsModified = observation.values
    return obsModified

def extract_from_excel(inFile, var, sites, sitetypes, plotmode=0):
    # inFile = path to input excel file
    # var = Variable object
    # sites = list of sites e.g. ['Sandnes', 'Iffiartafik', 'Qoornoq', 'Ersaa', 'Kangeq']
    # sitetypes = list of site types e.g. ['Cultural', 'Natural']
    # plotmode = integer defining how data should be plotted and treated in this function.

    dataList = []
    # read excel with pandas
    df = pd.read_excel(inFile, var.sheet, header=2, parse_cols='A:AZ', na_values='none')
    # group by excel column site
    for site in sites:
        sitegroup = df.groupby(['Site']).get_group(site)
        # group by type (Cultural/Natural)
        for sitetype in sitetypes:
            typegroup = sitegroup.groupby(['Type']).get_group(sitetype)
            # for scatter plot mean
            if int(plotmode) == 4:
                observation = data_transform(typegroup.iloc[:, var.column], var)
                dataList.append(Data(site, sitetype, 'all', observation))
            # for profile plot mean
            elif int(plotmode) == 2:
                depth = typegroup.iloc[:, 4].values
                observation = data_transform(typegroup.iloc[:, var.column], var)
                dataList.append(Data(site, sitetype, 'all', observation, depth))
            else:
                # group by plot number
                for plotNum in range(1, 7):
                    try:
                        plotgroup = typegroup.groupby(df.iloc[:, 3]).get_group(plotNum)
                        observation = data_transform(plotgroup.iloc[:, var.column], var)
                        if var.isdepth:
                            # with depths
                            depth = plotgroup.iloc[:, 4]
                            dataList.append(Data(site, sitetype, plotNum, observation, depth.values))
                        else:
                            # no depths - only one observation - therefore take zero index of array
                            dataList.append(Data(site, sitetype, plotNum, observation[0]))
                    except:
                        print 'no plot number ' + str(plotNum) + ' in ' + site + ' ' + sitetype
    # For profile plot mean. At selected site and sitetype all observations belonging to same depth
    # are pooled together to get mean and std..
    if int(plotmode) == 2:
        outList = []
    # Add plots together and calculate site mean of Cultural/Natural
        for data in dataList:
            depthDict = {5: [], 10: [], 20: [], 30: []}
            # append observations from same depth at all plots to dictionary
            for num in range(0, len(data.depth)):
                depthDict[data.depth[num]].append(data.observation[num])
            # calculate mean, standard deviation and number of elements and append to output dataList
            meanList = []
            stdList = []
            sizeList = []
            varList = []
            depthList = []
            for depth in [5, 10, 20, 30]:
                # Zeros are removed.
                # NB: if zero is a valid number this should be modified!
                a = np.asarray(depthDict[depth])
                a = a.ravel()[np.flatnonzero(a)]
                if a.size > 0:
                    # Check if mean is not nan (has to be there due to the Sandnes case where there are no observations
                    # at all in the 10 cm depth.
                    if not np.isnan(a[~np.isnan(a)].mean()):
                        meanList.append(a[~np.isnan(a)].mean())
                        stdList.append(a[~np.isnan(a)].std())
                        sizeList.append(a[~np.isnan(a)].size)
                        varList.append(a[~np.isnan(a)].var(ddof=1))
                        depthList.append(depth)
            outList.append(Data(data.site, data.sitetype, data.plot, {'mean': meanList, 'std': stdList, 'n': sizeList,
                                                                      'var': varList}, depthList))
        dataList = outList
    return dataList

def getdata(inFile, variable, sites, sitetypes, plotmode=0):
    # prepare list of sites and site types
    siteList = []
    if sites == 6:
        for num in range(1, 6):
            siteList.append(siteDict[num])
    else:
        siteList.append(siteDict[sites])

    if typeDict[sitetypes] == 'both':
        stypeList = [typeDict[1], typeDict[2]]
    else:
        stypeList = [typeDict[sitetypes]]
    var = Variable(variable)

    # extract data
    dataList = extract_from_excel(inFile, var, siteList, stypeList, plotmode)
    return dataList