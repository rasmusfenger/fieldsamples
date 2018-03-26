from loaddata import *
from dictionaries import *

# t-tests
def issig(p):
    if p <= 0.05:
        s = 'significant'
    elif p > 0.05:
        s = 'not significant'
    else:
        s = 'nan'
    return s

def ttest(ds, var, mode, savetxt=None, printtxt=False, equal_var=False):
    from scipy.stats import ttest_ind_from_stats
    # make text header
    header = var.title + ' t-test'

    dataList = ds.data
    if mode == 1:
        header += "\n%s vs %s\n" % (dataList[0].sitetype, dataList[1].sitetype)
    testresult = ''
    # loop through elements in datalists. They are organised so that 1st is tested against 2nd, 3rd against 4th etc.
    # therefore number of loopes = lenght of datalist divided by 2.
    c = 0
    for num in range(len(dataList)/2):
        statList = []
        # Get the descriptive statistics of a and b.
        amean = np.asarray(dataList[c].observation['mean'])
        avar = np.asarray(dataList[c].observation['var'])
        an = np.asarray(dataList[c].observation['n'])

        bmean = np.asarray(dataList[c+1].observation['mean'])
        bvar = np.asarray(dataList[c+1].observation['var'])
        bn = np.asarray(dataList[c+1].observation['n'])

        if var.isdepth == 'yes' and ds.di == False:
            # use indices to ensure data from right depths is used
            ai = 0
            for ad in dataList[c].depth:
                bi = 0
                for bd in dataList[c+1].depth:
                    if ad == bd:
                        # Use scipy.stats.ttest_ind_from_stats.
                        t, p = ttest_ind_from_stats(amean[ai], np.sqrt(avar[ai]), an[ai], bmean[bi], np.sqrt(bvar[bi]),
                                                    bn[bi], equal_var=equal_var)
                        statList.append(["%gcm:"%(ad),t,p,an[ai]])# [depth, t, p]
                    bi = bi + 1
                ai = ai + 1
        else:
            t, p = ttest_ind_from_stats(amean, np.sqrt(avar), an, bmean, np.sqrt(bvar), bn, equal_var=equal_var)
            statList.append(['', t, p, an])
        # make text with test results
        if mode == 1:
            testresult += "\n%s" % (dataList[c].site)
        elif mode == 2:
            testresult += "\n\n%s\n%s vs %s" % (dataList[c].sitetype, dataList[c].site, dataList[c + 1].site)
        for stat in statList:
            if mode == 1:
                testresult += ("\n%s\tt = %.3f     p = %.3f     n = %d     " % (stat[0], stat[1], stat[2], stat[3])) + issig(float(stat[2]))
            elif mode == 2:
                testresult += ("\n%s\t = %.3f     p = %.3f     n = %d     " % (stat[0], stat[1], stat[2], stat[3])) + issig(float(stat[2]))
        c += 2
    if printtxt:
        print header, testresult
    if savetxt:
        outFile = os.path.join(savetxt, var.title + '_t-test_' + statModeDict[mode] + '.txt')
        with open(outFile, 'w') as txt:
            txt.write(header + testresult)
        print 'Text-file created: ' + outFile

def ttest_manual(listA, listB, equal_var=True, print_it=True):
    from scipy.stats import ttest_ind
    t, p = ttest_ind(listA, listB, equal_var=equal_var)
    if print_it:
        print "\n%s\tt = %.3f  \tp = %.3f \tn = %d \t" % ('', t, p, len(listA)) + issig(float(p))
    return t, p

def ttest_stype(inFile, site, var, savetxt=None, printtxt=False, equal_var=False):
    # get data
    # distinguish between variables with depths and no depth. If depth, the values belong to a population of values
    # from the same depth. Eg. natural 10 cm (n=6) should be evaluated against cultural 10 cm. 5 and 10 cm can not be
    # evaluated together as they are not independant samples. So if variable has depth and depth has not been integrated
    # then each depth are evaluated against each other.
    sitetype = 3
    mode = 1
    if var.isdepth == 'yes' and var.di == False:
        ds = getData(inFile, var, site, sitetype, groupby='depth', mod=var.mod)
        ds.data = pool_depth(ds.data)
    else:
        ds = getData(inFile, var, site, sitetype, groupby='plot', mod=var.mod, di=var.di)
        ds.data = pool_plot(ds.data, stat=True)
    ttest(ds, var, mode, savetxt, printtxt, equal_var)

def ttest_site(inFile, site1, site2, stype, var, savetxt=None, printtxt=False, equal_var=False):
    # get data
    siteList = [siteDict[site1], siteDict[site2]]
    stypeList = [typeDict[stype]]
    mode = 2
    if var.isdepth == 'yes':
        ds = getData(inFile, var, siteList, stypeList, groupby='depth', mod=var.mod)
        ds.data = pool_depth(ds.data)
        #dataList = extract_from_excel(inFile, var, siteList, stypeList, 2)
    else:
        ds = getData(inFile, var, siteList, stypeList, groupby='depth', mod=var.mod)
        #dataList = extract_from_excel(inFile, var, siteList, stypeList, 4)
    ttest(ds, var, mode, savetxt, printtxt, equal_var)
