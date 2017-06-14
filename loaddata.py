import os
import sys
import pandas as pd
import numpy as np
from dictionaries import *
from scipy.interpolate import interp1d
from scipy.integrate import simps

class Dataset(object):
    def __init__(self, variable, dataList, mod, di):
        self.var = variable
        self.data = dataList
        self.mod = mod
        self.di = di

class Data(object):
    def __init__(self, site, sitetype, plot, observation, depth=None):
        self.site = site
        self.sitetype = sitetype
        self.observation = observation
        self.plot = plot
        self.depth = depth

class Variable(object):
    # Defines a variable class based on info in csv file in root.
    def __init__(self, variable, mod, di):
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
                self.mod = mod
                self.di = di

def getlog(dataList):
    # calculate log
    for data in dataList:
        data.observation = np.log10(np.asarray(data.observation) + 1)
    return dataList

def depth_integrate(dataList, depth):
    # integrate over depth
    for i in range(len(dataList)):
        x = dataList[i].depth
        y = dataList[i].observation
        for num in range(len(x)):
            if x[num] == 5:
                x = np.append(x, 0)
                y = np.append(y, y[num])
            if x[num] == max(x):
                x = np.append(x, max(x) + 5)
                y = np.append(y, y[num])
        x, y = (list(t) for t in zip(*sorted(zip(x, y))))
        f = interp1d(x, y)
        x2 = list(np.linspace(min(x), max(x), num=max(x)+1, endpoint=True))
        y2 = list(f(x2))
        # if depth is higher than data available, then use deepest depth
        if depth > max(x):
            depthUsed = max(x)
        else:
            depthUsed = depth
        depthIndex = x2.index(depthUsed) + 1
        intArea = simps(y2[:depthIndex], x2[:depthIndex])
        dataList[i].observation = [intArea]
        dataList[i].depth = [depthUsed]
    return dataList

def extract_from_excel(inFile, var, site, sitetype, groupby='plot'):
    # inFile = path to input excel file
    # var = Variable object
    # site = site number, see siteDict in dictionaries
    # sitetype = sitetype number, see siteDict in dictionaries
    siteList = []
    if site == 6:
        for num in range(1, 6):
            siteList.append(siteDict[num])
    else:
        siteList.append(siteDict[site])

    if typeDict[sitetype] == 'both':
        sitetypeList = [typeDict[1], typeDict[2]]
    else:
        sitetypeList = [typeDict[sitetype]]

    dataList = []
    # read excel with pandas
    df = pd.read_excel(inFile, var.sheet, header=2, parse_cols='A:AZ', na_values='none')
    # group by excel column site
    for site in siteList:
        sitegroup = df.groupby(['Site']).get_group(site)
        # group by type (Cultural/Natural)
        for sitetype in sitetypeList:
            typegroup = sitegroup.groupby(['Type']).get_group(sitetype)
            if groupby == 'sitetype':
                observation = typegroup.iloc[:, var.column]
                dataList.append(Data(site, sitetype, 'all', observation))
            elif groupby == 'plot':
                # group by plot number
                for plotNum in range(1, 7):
                    try:
                        plotgroup = typegroup.groupby(df.iloc[:, 3]).get_group(plotNum)
                        observation = plotgroup.iloc[:, var.column].values
                        if var.isdepth:
                            # with depths
                            depth = plotgroup.iloc[:, 4]
                            dataList.append(Data(site, sitetype, plotNum, observation, depth.values))
                        else:
                            # no depths - only one observation - therefore take zero index of array
                            dataList.append(Data(site, sitetype, plotNum, observation[0]))
                    except:
                        print 'no plot number ' + str(plotNum) + ' in ' + site + ' ' + sitetype
            elif groupby == 'depth':
                depth = typegroup.iloc[:, 4].values
                observation = typegroup.iloc[:, var.column].values
                dataList.append(Data(site, sitetype, 'all', observation, depth))
    return dataList

def pool_depth(dataList):
    # For profile plot mean. At selected site and sitetype all observations belonging to same depth
    # are pooled together to get mean and std. This is relevant in plotmode 2.
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
    return outList

def pool_plot(dataList):
    # Pooling together plots at each sitetype. Relevant in plotmode 4.
    outList = []
    for site in range(1,6):
        for stype in range(1,3):
            a = []
            for data in dataList:
                if data.site == siteDict[site] and data.sitetype == typeDict[stype]:
                    a.append(data.observation)
            a = np.asarray(a)
            if a.size > 0:
                mean = a[~np.isnan(a)].mean()
                std = a[~np.isnan(a)].std()
                size = a[~np.isnan(a)].size
                var = a[~np.isnan(a)].var(ddof=1)
                outList.append(Data(siteDict[site], typeDict[stype], 'all', {'mean': mean, 'std': std, 'n': size, 'var': var}))

    return outList

def getData(inFile, var, site, sitetype, groupby='plot', mod=False, di=False):
    dataList = extract_from_excel(inFile, var, site, sitetype, groupby=groupby)
    if mod:
        # other calculations can be added here
        if mod == 'log':
            dataList = getlog(dataList)
    if di:
        if groupby == 'plot' and var.isdepth == 'yes':
            dataList = depth_integrate(dataList, di)
        else:
            print 'Error: Cannot make depth integration. Make sure groupby="plot" and variable has depth observations'
            sys.exit(0)
    ds = Dataset(var, dataList, mod, di)
    return ds
