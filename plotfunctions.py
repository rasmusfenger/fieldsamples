import matplotlib.pyplot as plt
from scipy import stats
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
from loaddata import *
from dictionaries import *

########################################################################################################################
# Check input:
def check_input(inFile, site, stype, var1, var2, plotmode, savefig):
    def print_error(errList):
        # Error messages
        errMes = {1: 'inFile does not exist',
                  2: 'site not valid',
                  3: 'sitetype not valid',
                  4: 'plotmode not valid',
                  5: 'variable_1 not valid',
                  6: 'variable_2 not valid',
                  7: 'selected variable_1 cannot be combined with plotmode 1 or 2',
                  8: 'selected variable_1 cannot be combined with plotmode 4 unless it is depth integrated',
                  9: 'selected variable_2 cannot be combined with plotmode 4 unless it is depth integrated',
                  10: 'path for saving figure does not exist'}
        print 'Error - Wrong input!'
        for err in errList:
            print errMes[err]
        sys.exit(0)

    # Valid parameters
    plotmodeValid = ['1', '2', '2.1', '2.2', '2.3', '2.4', '2.5', '3', '3.1', '4', '4.1', '4.2', '4.3']

    errList = []
    # First check input parameters
    if not os.path.isfile(inFile):
        errList.append(1)
    if not site in siteDict:
        errList.append(2)
    if not stype in typeDict:
        errList.append(3)
    if not str(plotmode) in plotmodeValid:
        errList.append(4)
    if savefig:
        if not os.path.isdir(savefig):
            errList.append(10)
    if errList:
        print_error(errList)
    # Then check combination of input parameters
    else:
        if int(plotmode) == 1 or int(plotmode) == 2:
            #variable_1 has to have depth observations
            if var1.isdepth == 'no':
                errList.append(7)
        elif int(plotmode) == 4:
            # variable_1 and variable_2 cannot have depth observations unless they have been depth integrated
            if var1.isdepth == 'yes' and var1.di == False:
                errList.append(8)
            if var2.isdepth == 'yes' and var2.di == False:
                errList.append(9)
        if errList:
            print_error(errList)

########################################################################################################################
# plotting

def convertDataType(siteType):
    if siteType == 'Cultural':
        convertedType = 'archaeology'
    elif siteType == 'Natural':
        convertedType = 'reference'
    return convertedType

def layout(figname, xlabel, ylabel, plotmode, xlim, ylim, invertY, text, savefig, title, legend, size, grid, textnote):
    # define plot layout
    if xlabel:
        plt.gca().set_xlabel(xlabel)
    if ylabel:
        plt.gca().set_ylabel(ylabel)
    if size:
        plt.gcf().set_size_inches(size[0],size[1])
    if title:
        if title == True:
            plt.gca().set_title(figname, fontname='Arial')
        else:
            plt.gca().set_title(title, fontname='Arial')
    if xlim:
        plt.xlim(xlim)
    if ylim:
        plt.ylim(ylim)
    if legend:
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        if legend == 'special_1':
            legend_elements = [Patch(facecolor=cDict['Sandnes'], label='Sandnes'),
                               Patch(facecolor=cDict['Iffiartafik'], label='Iffiartafik'),
                               Patch(facecolor=cDict['Qoornoq'], label='Qoornoq'),
                               Patch(facecolor=cDict['Ersaa'], label='Ersaa'),
                               Patch(facecolor=cDict['Kangeq'], label='Kangeq'),
                               Line2D([0], [0], marker=cDict['CulturalM'], color='w', label='Archaeological site',
                                      markerfacecolor='none', markeredgecolor='black', markersize=7),
                               Line2D([0], [0], marker=cDict['NaturalM'], color='w', label='Reference area',
                                      markerfacecolor='none', markeredgecolor='black', markersize=7)]
            #Line2D([0], [0], color='red', lw=4, label='2 std.dev. Archaeological site')
            lgd = plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
        elif legend == 'special_2':
            legend_elements = [Line2D([5], [5], marker=cDict['CulturalM'], color='black', label='Archaeological site',
                                      markersize=7, markeredgecolor='black', markerfacecolor='white'),
                               Line2D([], [], marker=cDict['NaturalM'], color='black', label='Reference area',
                                      markersize=7, markeredgecolor='black', markerfacecolor='white', linestyle='--')]
            lgd = plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, -0.2), borderaxespad=0.)
        else:
            # anchor legend box
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if invertY:
        # invert y-axis (for profile plots)
        plt.gca().invert_yaxis()
        plt.gca().set_ylim([31, 4])
    if text:
        # placing text. Used for r2 value when plotting regression line
        at = AnchoredText(text, prop=dict(size=10), frameon=False, loc=2)
        plt.gca().add_artist(at)
    if grid:
        plt.gca().set_axisbelow(True)
        plt.gca().grid()
    if textnote:
        t = plt.gca().text(textnote[0], textnote[1], textnote[2], fontsize=textnote[3], transform=plt.gca().transAxes)
    if savefig:
        dir = os.path.join(savefig, 'plotmode_' + str(plotmode))
        if not os.path.isdir(dir):
            os.mkdir(dir)
        fname = os.path.join(dir, figname + '.png')
        if legend:
            plt.savefig(fname, dpi=1000, bbox_extra_artists = (lgd, t), bbox_inches = 'tight')
        else:
            plt.savefig(fname, dpi=1000, bbox_inches='tight')
        # if dpi should be the same as plt.show then use: dpi=plt.gcf().dpi
    plt.show()

def plot_profile(ds, figname, plotmode, xlim, ylim, savefig, title, legend, size, grid, textnote):
    # define axis labels
    xlabel = ds.var.xname
    if ds.mod:
        xlabel += '- ' + ds.mod
    ylabel = ds.var.yname
    # distinguish between plotmode 1 and 2
    dataList = ds.data
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
        fig, axes = plt.subplots(1, len(dataList)/2, sharey=True, sharex=True)
        if len(dataList) > 2:
            axes_list = [item for item in axes]
        else:
            axes_list = [axes]
        legendList = []
        leglabelList = []
        plot_number = 0
        for data in reversed(dataList):
            x = np.asarray(data.observation['mean'])
            y = np.asarray(data.depth)
            std = np.asarray(data.observation['std'])
            n = np.asarray(data.observation['n'])
            labelname = data.site + ' ' + convertDataType(data.sitetype)
            ax = axes_list[int(plot_number)]
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
                zerotup = ()
                for elem in std:
                    zerotup += (0,)
                if data.sitetype == 'Natural':
                    std = std * -1
                xerr = [zerotup, std]
                eb = ax.errorbar(x, y, xerr=xerr, ls=cDict[data.sitetype], c=cDict[data.site],
                                  marker=cDict[data.sitetype + 'M'], capsize=3)#, linewidth=2.0, markersize=10.0)
                if data.sitetype == 'Natural':
                    try:
                        eb[-1][0].set_linestyle('--')
                    except:
                        pass
                legendList.append(eb)
                leglabelList.append(labelname)
            # add standard error
            elif plotmode == 2.4:
                se = std/np.sqrt(n)
                zerotup = ()
                for elem in se:
                    zerotup += (0,)
                if data.sitetype == 'Natural':
                    se = se * -1
                xerr = [zerotup, se]
                eb = ax.errorbar(x, y, xerr=xerr, ls=cDict[data.sitetype], c=cDict[data.site],
                                  marker=cDict[data.sitetype + 'M'], capsize=3)#, linewidth=2.0, markersize=10.0)
                if data.sitetype == 'Natural':
                    try:
                        eb[-1][0].set_linestyle('--')
                    except:
                        pass
                legendList.append(eb)
                leglabelList.append(labelname)
            elif plotmode == 2.5:
                se = std/np.sqrt(n)
                zerotup = ()
                for elem in se:
                    zerotup += (0,)
                if data.sitetype == 'Natural':
                    se = se * -1
                xerr = [zerotup, se]
                eb = ax.errorbar(x, y, xerr=xerr, ls=cDict[data.sitetype], c=cDict[data.site],
                                  marker=cDict[data.sitetype + 'M'], capsize=3)#, linewidth=2.0, markersize=10.0)
                if data.sitetype == 'Natural':
                    try:
                        eb[-1][0].set_linestyle('--')
                    except:
                        pass
                legendList.append(eb)
                leglabelList.append(labelname)
                yticksList = ['','3-8','8-13','','18-23','','28-33','']
                #yticksList = ['', '', '', '', '', '', '', '']
                ax.set_yticklabels(yticksList)

            if title:
                ax.set_title(data.site)
            # set y axis label on only first subplot
            if plot_number == 0:
                ax.set_ylabel(ylabel)
            plot_number += 0.5
        # set x axis label
        fig.text(0.5, -0.05, xlabel, ha='center')
        # define legend
        if legend == True:
            if len(axes_list) == 5:
                legbox_xshif = 0.15
            else:
                legbox_xshif = 0
            lgd = axes_list[0].legend(legendList, leglabelList, loc='upper left', bbox_to_anchor=(legbox_xshif, -0.3),
                                   ncol=len(axes_list), fancybox=True, shadow=True)
            legend = None
        ylabel = None
        xlabel = None
        title = None
        layout(figname, xlabel, ylabel, plotmode, xlim, ylim, invertY=True, text=None, savefig=savefig, title=title, legend=legend, size=size, grid=grid, textnote=textnote)


def plot_scatter(dsX, dsY, figname, plotmode, xlim, ylim, reg, savefig, title, legend, size, grid, textnote):
    # define axis labels
    xlabel = dsX.var.xname
    if dsX.di:
        #xlabel = xlabel.replace('^3','^2')
        xlabel += ' in ' + str(dsX.di) + ' cm'
    if dsX.mod:
        xlabel += '- ' + dsX.mod
    ylabel = dsY.var.xname
    if dsY.di:
        #ylabel = ylabel.replace('^3', '^2')
        ylabel += ' in ' + str(dsY.di) + ' cm'
    if dsY.mod:
        ylabel += '- ' + dsY.mod
    dataListX = dsX.data
    dataListY = dsY.data
    # prepare lists for saving data for calculating regression line
    fitListX = []
    fitListY = []
    if int(plotmode) == 3:
        # Scatter plot of all observations
        labelList = []
        dimcheck = ''
        # collect cultural observations and natural observations in two lists (only relevant for plotmode 3.1)
        culList = []
        natList = []
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
            # only relevant for plotmode 3.1
            if x.sitetype == 'Cultural':
                culList.append([x.observation[0],y.observation[0]])
            elif x.sitetype == 'Natural':
                natList.append([x.observation[0],y.observation[0]])
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
        if title == False:
            if len(dataListX) == 60:
                title = 'All'
            else:
                title = x.site
        if dimcheck != '':
            print dimcheck + ' have more than 1 data record per point. Values have been summed'
        if plotmode == 3.1:
            # add ellipse equaling 2 standard deviations (95% conf interval)
            from addellipse import plot_point_cov
            plot_point_cov(np.array(culList), nstd=2, alpha=0.5, edgecolor='r', facecolor='none')
            plot_point_cov(np.array(natList), nstd=2, alpha=0.5, edgecolor='g', facecolor='none')


    elif int(plotmode) == 4:
        # Scatter plot of mean per site and sitetype
        for num in range(0, len(dataListX)):
            x = dataListX[num]
            y = dataListY[num]
            labelname = x.site + ' ' + x.sitetype
            if plotmode == 4:
                plt.scatter(x.observation['mean'], y.observation['mean'], c=cDict[x.site],
                            marker=cDict[x.sitetype + 'M'], label=labelname)
            elif 4.1 <= plotmode <= 4.3:
                # add errorbars
                if plotmode == 4.1:
                    ystd = y.observation['std']
                    xstd = None
                elif plotmode == 4.2:
                    ystd = None
                    xstd = x.observation['std']
                elif plotmode == 4.3:
                    ystd = y.observation['std']
                    xstd = x.observation['std']
                eb = plt.errorbar(x.observation['mean'], y.observation['mean'], yerr=ystd,
                                  xerr=xstd, ls=cDict[x.sitetype], c=cDict[x.site], label=labelname,
                                  marker=cDict[x.sitetype + 'M'])
                # modify errorbar linestyle
                if x.sitetype == 'Natural':
                    eb[-1][0].set_linestyle('--')
                    if plotmode == 4.3:
                        eb[-1][1].set_linestyle('--')
            fitListX.append(x.observation['mean'])
            fitListY.append(y.observation['mean'])

    # Add regression line
    if reg:
        fitListX = np.asarray(fitListX)
        fitListY = np.asarray(fitListY)
        fit = np.polyfit(fitListX, fitListY, 1)
        plt.plot(fitListX, fit[0] * fitListX + fit[1], color='black')
        slope, intercept, r_value, p_value, std_err = stats.linregress(fitListX, fitListY)
        text = '$R^2$ = '+'{0:.2f}'.format(r_value*r_value) + '\np   = '+'{0:.3f}'.format(p_value)
    else:
        text = None
    layout(figname, xlabel, ylabel, plotmode, xlim, ylim, invertY=False, text=text, savefig=savefig, title=title,
           legend=legend, size=size, grid=grid, textnote=textnote)

def plot(inFile, site, stype, var1, var2, plotmode, xlim=None, ylim=None, reg=False, savefig=None, title=True, legend=True, size=None, grid=None, textnote=None):
    # check input parameters
    check_input(inFile, site, stype, var1, var2, plotmode, savefig)

    # Soil profile plots
    if int(plotmode) <= 2:
        figname = var1.title + ' ' + siteDict[site]
        if int(plotmode) == 1:
            ds = getData(inFile, var1, site, stype, groupby='plot', mod=var1.mod, di=False)
        elif int(plotmode) == 2:
            ds = getData(inFile, var1, site, stype, groupby='depth', mod=var1.mod, di=False)
            ds.data = pool_depth(ds.data)
        plot_profile(ds, figname, plotmode, xlim, ylim, savefig, title, legend, size, grid, textnote)

    # Scatter plots
    elif int(plotmode) >= 3:
        figname = var1.title + '(x) vs ' + var2.title + '(y)' + ' ' + siteDict[site]
        dsX = getData(inFile, var1, site, stype, groupby='plot', mod=var1.mod, di=var1.di)
        dsY = getData(inFile, var2, site, stype, groupby='plot', mod=var2.mod, di=var2.di)
        if int(plotmode) == 4:
            dsX.data = pool_plot(dsX.data, stat=True)
            dsY.data = pool_plot(dsY.data, stat=True)
        plot_scatter(dsX, dsY, figname, plotmode, xlim, ylim, reg, savefig, title, legend, size, grid, textnote)
