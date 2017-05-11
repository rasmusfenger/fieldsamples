import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText

########################################################################################################################
# How to use:
##############
# Sites:
# 1 = Sandnes
# 2 = Iffiartafik
# 3 = Qoornoq
# 4 = Ersaa
# 5 = Kangeq
# 6 = all
# 7 = all_separate
#
# Types:
# Natural = 1
# Cultural = 2
# both = 3
#
# Variables:
# NB: to use log(variable) add 0.1 to variable number
# 1 = soil water content
# 2 = pH
# 6 = Soil weight
# 7 = Remaining soil after sifting
# 8 = waste by sifting
# 10 = Roots < 1mm (dry)
# 11 = Roots > 1mm (dry)
# 12 = Horse tail (dry)
# 13 = Roots < 1mm (dry) /kg dry soil
# 14 = Roots > 1mm (dry) /kg dry soil
# 15 = Horse tail (dry) /kg dry soil
# 20 = Total biomass
# 21 = NDVI handheld
# 22 = LAI
# 30 = Phosphor concentration in analysis
# 31 = Phosphor/kg dry soil
# 32 = Phosphor/kg dry soil - blank corrected
# 40 = NO3 concentration in analysis
# 41 = NH4 concentration in analysis
# 42 = TOC concentration in analysis
# 43 = TN concentration in analysis
# 44 = NO3 in dry soil, blank corrected
# 45 = NH4 in dry soil, blank corrected
# 46 = TN in dry soil, blank corrected (Total nitrogen)
# 47 = DON in dry soil, blank corrected (Dissolved organic nitrogen, eg. aminosyrer)
# 48 = TOC in dry soil, blank corrected (Total organic carbon)

# plot modes:
# 1 = all plots

# 2 = pool natural/cultural plots together and plot mean
# 2.1 = add std as error plot
# 2.2 = add std as shaded area

# 3 = Scatter plot

# 4 = Scatter plot mean
# 4.1 = add std error bar on y-axis
# 4.2 = add std error bar on x-axis
# 4.3 = add std error bar on both axes

# Code example:
'''
from plotfunctions import *
%matplotlib inline

inFile = '/Users/rasmus/Desktop/Lab_sheet_v9.16.xlsx'
sites = 6
types = 3
variable_1 = 7
variable_2 = 6.1
plotmode = 4.1
reg = True

################
if sites == 7:
    for num in range(1,7):
        plot(inFile, num, types, variable_1, variable_2, plotmode, reg)
else:
    plot(inFile, sites, types, variable_1, variable_2, plotmode, reg)
'''
########################################################################################################################

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
    variableValid = [1,2,3,4,5,6,7,8,10,11,12,13,14,15,20,21,22,30,31,32,40,41,42,43,44,45,46,47,48,49]
    plotmodeValid = ['1', '2', '2.1', '2.2', '3', '4', '4.1', '4.2', '4.3']
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

#def test(inFile):
#    siteList = [1,2,3,4,5,6]
#    variableList = [1,2,3,4,5,6,7,8,20,21,22]
#    plotmodeList = [1, 2, 2.1, 2.2, 3, 4, 4.1, 4.2, 4.3]

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

########################################################################################################################
# plotting
def layout(title, xlabel, ylabel, plotmode, invertY=False, text=None, savefig=None):
    # define plot layout
    plt.gca().set_title(title)
    plt.gca().set_xlabel(xlabel)
    plt.gca().set_ylabel(ylabel)
    # anchor legend box
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if invertY:
        # invert y-axis (for profile plots)
        plt.gca().invert_yaxis()
        plt.gca().set_ylim([31, 4])
    if text:
        # placing text. Used for r2 value when plotting regression line
        at = AnchoredText(text, prop=dict(size=10), frameon=False, loc=2,)
        plt.gca().add_artist(at)
    if savefig:
        dir = os.path.join(savefig, 'plotmode_' + str(plotmode))
        if not os.path.isdir(dir):
            os.mkdir(dir)
        fname = os.path.join(dir, title + '.png')
        plt.savefig(fname, dpi=150, bbox_extra_artists = (lgd,), bbox_inches = 'tight')
        # if dpi should be the same as plt.show then use: dpi=plt.gcf().dpi
    plt.show()

def plot_profile(dataList, title, xlabel, ylabel, plotmode, savefig):
    if plotmode == 1:
        if len(dataList) > 48:
            sites = 'all'
        else:
            sites = ''
        labelList = []
        for data in dataList:
            x = data.observation
            y = data.depth
            # Only plot data if list is not only nans/zeros
            if np.isnan(x).all() == False and np.any(x):
                # sort data based on y (depth) to plot the profile correctly
                y, x = (list(t) for t in zip(*sorted(zip(y, x))))
                # when observations from all sites - label just site and type
                if sites == 'all':
                    labelname = data.site + ' ' + data.sitetype
                    if labelname in labelList:
                        plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], label='_none')
                    else:
                        plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname)
                        labelList.append(labelname)
                # when observations from 1 site - label plot number
                else:
                    labelname = 'Plot' + ' ' + str(data.plot) + ' ' + data.sitetype
                    col = cDict['plot' + str(data.plot)]
                    plt.plot(x, y, ls=cDict[data.sitetype], c=col, label=labelname)
    elif int(plotmode) == 2:
        for data in dataList:
            x = np.asarray(data.observation['mean'])
            y = np.asarray(data.depth)
            std = np.asarray(data.observation['std'])
            labelname = data.site + ' ' + data.sitetype + ' mean'
            if plotmode == 2:
                plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname, marker='o')
            elif plotmode == 2.1:
                # add error bar based on std
                eb = plt.errorbar(x, y, xerr=std, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname,
                                  marker='o')
                if data.sitetype == 'Natural':
                    eb[-1][0].set_linestyle('--')
            elif plotmode == 2.2:
                # add shaded area based on std
                plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname, marker='o')
                plt.fill_betweenx(y, x - std, x + std, color=cDict[data.site], alpha=0.1)
    layout(title, xlabel, ylabel, plotmode, invertY=True, savefig=savefig)


def plot_scatter(dataListX, dataListY, title, xlabel, ylabel, plotmode, reg, savefig):
    # prepare lists for saving data for calculating regression line
    fitListX = []
    fitListY = []
    if int(plotmode) == 3:
        # Scatter plot of all observations
        labelList = []
        dimcheck = ''
        for num in range(0, len(dataListX)):
            x = dataListX[num]
            y = dataListY[num]
            # Check if dimensions fit. If not, sum observations from the variable with more observations.
            # This is relevant when variables with observations from several depths (e.g. soil moisture) are plotted
            # agains a variable with only one observation (e.g. biomass). A print statement is made if this modification
            # is done.
            if len(x.observation) == 1 and len(y.observation) > 1:
                y.observation = [np.sum(y.observation)]
                dimcheck = 'y-values'
            elif len(x.observation) > 1 and len(y.observation) == 1:
                x.observation = [np.sum(x.observation)]
                dimcheck = 'x-values'
            # plot data and label only based on site and sitetype
            labelname = x.site + ' ' + x.sitetype
            if labelname in labelList:
                plt.scatter(x.observation, y.observation, c=cDict[x.site], marker=cDict[x.sitetype + 'M'], label='_none')
            else:
                plt.scatter(x.observation, y.observation, c=cDict[x.site], marker=cDict[x.sitetype + 'M'], label=labelname)
                labelList.append(labelname)
            # save plotted data in list for calculating regression line
            for num in range(0, len(x.observation)):
                # ensure that pairs consist of real numbers and not nan
                if np.isnan(x.observation[num]) == False and np.isnan(y.observation[num]) == False:
                    fitListX.append(x.observation[num])
                    fitListY.append(y.observation[num])
        if dimcheck != '':
            print dimcheck + ' have more than 1 data record per point. Values have been summed'

    elif int(plotmode) == 4:
        # Scatter plot of mean per site and sitetype
        for num in range(0, len(dataListX)):
            x = dataListX[num]
            y = dataListY[num]
            labelname = x.site + ' ' + x.sitetype
            if plotmode == 4:
                plt.scatter(np.mean(x.observation), np.mean(y.observation), c=cDict[x.site],
                            marker=cDict[x.sitetype + 'M'], label=labelname)
            elif 4.1 <= plotmode <= 4.3:
                # add errorbars
                if plotmode == 4.1:
                    ystd = np.std(y.observation)
                    xstd = None
                elif plotmode == 4.2:
                    ystd = None
                    xstd = np.std(x.observation)
                elif plotmode == 4.3:
                    ystd = np.std(y.observation)
                    xstd = np.std(x.observation)
                eb = plt.errorbar(np.mean(x.observation), np.mean(y.observation), yerr=ystd,
                                  xerr=xstd, ls=cDict[x.sitetype], c=cDict[x.site], label=labelname,
                                  marker='o')
                # modify errorbar linestyle
                if x.sitetype == 'Natural':
                    eb[-1][0].set_linestyle('--')
            fitListX.append(np.mean(x.observation))
            fitListY.append(np.mean(y.observation))

    # Add regression line
    if reg:
        fitListX = np.asarray(fitListX)
        fitListY = np.asarray(fitListY)
        fit = np.polyfit(fitListX, fitListY, 1)
        plt.plot(fitListX, fit[0] * fitListX + fit[1], color='black')
        slope, intercept, r_value, p_value, std_err = stats.linregress(fitListX, fitListY)
        text = 'r2 = '+'{0:.2f}'.format(r_value*r_value)
    else:
        text = None
    layout(title, xlabel, ylabel, plotmode, invertY=False, text=text, savefig=savefig)

def plot(inFile, site, stype, variable_1, variable_2, plotmode, reg=False, savefig=None):
    # check input parameters
    check_input(inFile, site, stype, variable_1, variable_2, plotmode, savefig)
    # prepare list of sites
    siteList = []
    if site == 6:
        for num in range(1,6):
            siteList.append(siteDict[num])
    else:
        siteList.append(siteDict[site])

    if typeDict[stype] == 'both':
        stypeList = [typeDict[1], typeDict[2]]
    else:
        stypeList = [typeDict[stype]]

    # Soil profile plots
    var1 = Variable(variable_1)
    title = var1.title + ' ' + siteDict[site]
    dataListX = extract_from_excel(inFile, var1, siteList, stypeList, plotmode)
    if int(plotmode) <= 2:
        plot_profile(dataListX, title, var1.xname, var1.yname, plotmode, savefig)

    # Scatter plots
    elif int(plotmode) >= 3:
        var2 = Variable(variable_2)
        title = var1.title  + '(x) vs ' + var2.title + '(y)'
        dataListY = extract_from_excel(inFile, var2, siteList, stypeList, plotmode)
        plot_scatter(dataListX, dataListY, title, var1.xname, var2.xname, plotmode, reg, savefig)

# saving plots to pdf
def plot2pdf(inFileList, outFilename, title):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch, cm
    from reportlab.lib.pagesizes import letter, landscape

    if len(inFileList) > 0:
        c = canvas.Canvas(outFilename, pagesize=landscape(letter))
        figsizex = 13
        figsizey = 6.5
        figlocList = [[0.5, 13.5], [14.5, 13.5], [0.5, 7], [14.5, 7], [0.5, 0.5], [14.5, 0.5]]
        for num in range(0, len(inFileList)):
            c.drawImage(inFileList[num], figlocList[num][0] * cm, figlocList[num][1] * cm, figsizex * cm, figsizey * cm)
        c.setFont('Helvetica', 16)
        c.drawString(0.5*cm, 20.5*cm, title)
        c.showPage()
        c.save()
        print 'PDF-file created: ' + outFilename
    else:
        print 'Could not create PDF-file - figures not available'

def plot2pdf_allsites(variable, plotmode, inFolder, outFolder):
    var = Variable(variable)
    sites = 6
    outFilename = os.path.join(outFolder, var.title + ' ' + siteDict[sites] + '.pdf')
    inFileList = []
    for num in range(1,7):
        inFile = os.path.join(inFolder, 'plotmode_' + str(plotmode), var.title + ' ' + siteDict[num] + '.png')
        if os.path.isfile(inFile):
            inFileList.append(inFile)
        else:
            print 'figure does not exist: ' + inFile
    title = var.title + ' ' + siteDict[num]
    plot2pdf(inFileList, outFilename, title)

def plot2pdf_onesite(site, variableList, plotmode, inFolder, outFolder, plotname):
    inFileList = []
    outFilename = os.path.join(outFolder, plotname + ' ' + siteDict[site] + '.pdf')
    for variable in variableList:
        var = Variable(variable)
        inFile = os.path.join(inFolder, 'plotmode_' + str(plotmode), var.title + ' ' + siteDict[site] + '.png')
        if os.path.isfile(inFile):
            inFileList.append(inFile)
        else:
            print 'figure does not exist: ' + inFile
    title = plotname + ' ' + siteDict[site]
    plot2pdf(inFileList, outFilename, title)

########################################################################################################################
# t-tests
def writetxt(outFile, mode, type, dataList, statList, var):
    with open(outFile, mode) as txt:
        if type == 'cultural_vs_natural':
            if mode == 'w':
                txt.write(var.title + 't-test')
            txt.write("\n\n%s" % (dataList[0].site))
            txt.write("\n%s vs %s" % (dataList[0].sitetype, dataList[1].sitetype))
        elif type == 'site_vs_site':
            if mode == 'w':
                txt.write(var.title + 't-test')
            txt.write("\n\n%s" % (dataList[0].sitetype))
            txt.write("\n%s vs %s" % (dataList[0].site, dataList[1].site))
        for stat in statList:
            txt.write("\n%gcm: \tt = %.5f  \tp = %.5f \t%s" % (stat[0], stat[1], stat[2], stat[3]))
    if mode == 'w':
        print 'Text-file created: ' + outFile

def ttest(dataList, type, var, savetxt=None, printtxt=False):
    from scipy.stats import ttest_ind_from_stats
    # Get the descriptive statistics of a and b.
    amean = np.asarray(dataList[0].observation['mean'])
    avar = np.asarray(dataList[0].observation['var'])
    an = np.asarray(dataList[0].observation['n'])

    bmean = np.asarray(dataList[1].observation['mean'])
    bvar = np.asarray(dataList[1].observation['var'])
    bn = np.asarray(dataList[1].observation['n'])

    statList = []
    # use indices to ensure data form right depths is used
    ai = 0
    for ad in dataList[0].depth:
        bi = 0
        for bd in dataList[1].depth:
            if ad == bd:
                # Use scipy.stats.ttest_ind_from_stats.
                t, p = ttest_ind_from_stats(amean[ai], np.sqrt(avar[ai]), an[ai], bmean[bi], np.sqrt(bvar[bi]), bn[bi],
                                            equal_var=False)
                if p <= 0.05:
                    s = 'significant'
                elif p > 0.05:
                    s = 'not significant'
                else:
                    s = 'nan'
                statList.append([ad,t,p,s])
            bi = bi + 1
        ai = ai + 1
    if printtxt:
        if type == 'cultural_vs_natural':
            print "\n%s" % (dataList[0].site)
            print "%s vs %s" % (dataList[0].sitetype, dataList[1].sitetype)
        elif type == 'site_vs_site':
            print "\n%s" % (dataList[0].sitetype)
            print "%s vs %s" % (dataList[0].site, dataList[1].site)
        for stat in statList:
            print("%gcm: \tt = %.5f  \tp = %.5f \t%s" % (stat[0], stat[1], stat[2], stat[3]))
    if savetxt:
        outFile = os.path.join(savetxt, var.title + '_t-test_' + type + '.txt')
        if os.path.isfile(outFile):
            with open(outFile, 'r') as txt:
                if len(txt.readlines()) > 10000:
                    writetxt(outFile, 'w', type, dataList, statList, var)
                else:
                    writetxt(outFile, 'a', type, dataList, statList, var)
        else:
            writetxt(outFile, 'w', type, dataList, statList, var)

def ttest_stype(inFile, site, variable, savetxt=None, printtxt=False):
    # check input parameters
    # To be done

    # get data
    var = Variable(variable)
    siteList = [siteDict[site]]
    stypeList = [typeDict[1], typeDict[2]]
    dataList = extract_from_excel(inFile, var, siteList, stypeList, 2)
    ttest(dataList, 'cultural_vs_natural', var, savetxt, printtxt)

def ttest_site(inFile, site1, site2, stype, variable, savetxt=None, printtxt=False):
    # check input parameters
    # To be done

    # get data
    var = Variable(variable)
    siteList = [siteDict[site1], siteDict[site2]]
    stypeList = [typeDict[stype]]
    dataList = extract_from_excel(inFile, var, siteList, stypeList, 2)
    ttest(dataList, 'site_vs_site', var, savetxt, printtxt)

########################################################################################################################
# dictionaries
# dictionary with layout parameters
cDict = {'Sandnes': 'red',
         'Iffiartafik': 'green',
         'Qoornoq': 'blue',
         'Ersaa': 'cyan',
         'Kangeq': 'magenta',
         'Cultural': '-',
         'Natural': '--',
         'plot1': 'red',
         'plot2': 'green',
         'plot3': 'blue',
         'plot4': 'cyan',
         'plot5': 'magenta',
         'plot6': 'yellow',
         'CulturalM': 'x',
         'NaturalM': 'o'}

# dictionary with site names
siteDict = {1: 'Sandnes',
            2: 'Iffiartafik',
            3: 'Qoornoq',
            4: 'Ersaa',
            5: 'Kangeq',
            6: 'all sites'}

# dictionary with sitetype names
typeDict = {1: 'Natural',
            2: 'Cultural',
            3: 'both'}

########################################################################################################################
########################################################################################################################