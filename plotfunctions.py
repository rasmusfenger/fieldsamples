import matplotlib.pyplot as plt
from scipy import stats
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
from loaddata import *
from dictionaries import *

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

def layout2(title, xlabel, ylabel, plotmode, site, xlim, invertY=False, savefig=None):
    fig = plt.gcf()
    fig.set_size_inches(2.5, 2.5)
    plt.gca().set_xlabel(xlabel)
    plt.gca().set_title(site)
    if xlim:
        min = xlim/15
        plt.xlim([-min,xlim])
    if site == 'Kangeq':
        plt.gca().set_ylabel(ylabel)
    else:
        # plt.yticks([])
        plt.yticks([5,10,15,20,25,30,35], " ")
    if invertY:
        # invert y-axis (for profile plots)
        plt.gca().invert_yaxis()
        plt.gca().set_ylim([31, 4])

    if savefig:
        dir = os.path.join(savefig, 'plotmode_' + str(plotmode))
        if not os.path.isdir(dir):
            os.mkdir(dir)
        fname = os.path.join(dir, title + '.png')
        plt.savefig(fname, dpi=150)
        # if dpi should be the same as plt.show then use: dpi=plt.gcf().dpi
    plt.show()

def plot_profile(dataList, title, xlabel, ylabel, plotmode, xlim, savefig):
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
                plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname,
                         marker=cDict[data.sitetype + 'M'])
            elif plotmode == 2.1:
                # add error bar based on std
                eb = plt.errorbar(x, y, xerr=std, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname,
                                  marker=cDict[data.sitetype + 'M'])
                if data.sitetype == 'Natural':
                    eb[-1][0].set_linestyle('--')
            elif plotmode == 2.2:
                # add shaded area based on std
                plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], label=labelname,
                         marker=cDict[data.sitetype + 'M'])
                plt.fill_betweenx(y, x - std, x + std, color=cDict[data.site], alpha=0.1)
            elif plotmode == 2.3:
                #plt.plot(x, y, ls=cDict[data.sitetype], c=cDict[data.site], marker=cDict[data.sitetype + 'M'])
                zerotup = ()
                for elem in std:
                    zerotup += (0,)
                if data.sitetype == 'Natural':
                    std = std * -1
                xerr = [zerotup, std]
                eb = plt.errorbar(x, y, xerr=xerr, ls=cDict[data.sitetype], c=cDict[data.site],
                                  marker=cDict[data.sitetype + 'M'], capsize=3)#, linewidth=2.0, markersize=10.0)
                if data.sitetype == 'Natural':
                    eb[-1][0].set_linestyle('--')

    if plotmode < 2.3:
        layout(title, xlabel, ylabel, plotmode, invertY=True, savefig=savefig)
    else:
        layout2(title, xlabel, ylabel, plotmode, data.site, xlim, invertY=True, savefig=savefig)


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

def plot(inFile, site, stype, variable_1, variable_2, plotmode, xlim=None, reg=False, savefig=None):
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
        plot_profile(dataListX, title, var1.xname, var1.yname, plotmode, xlim, savefig)

    # Scatter plots
    elif int(plotmode) >= 3:
        var2 = Variable(variable_2)
        title = var1.title  + '(x) vs ' + var2.title + '(y)'
        dataListY = extract_from_excel(inFile, var2, siteList, stypeList, plotmode)
        plot_scatter(dataListX, dataListY, title, var1.xname, var2.xname, plotmode, reg, savefig)
