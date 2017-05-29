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

def ttest(dataList, mode, var, savetxt=None, printtxt=False):
    from scipy.stats import ttest_ind, ttest_ind_from_stats
    # make text header
    header = var.title + ' t-test'
    testresult = ''
    # loop through elements in datalists. They are organised so that 1st is tested against 2nd, 3rd against 4th etc.
    # therefore number of loopes = lenght of datalist divided by 2.
    c = 0
    for num in range(len(dataList)/2):
        statList = []
        if var.isdepth == 'yes':
            # Get the descriptive statistics of a and b.
            amean = np.asarray(dataList[c].observation['mean'])
            avar = np.asarray(dataList[c].observation['var'])
            an = np.asarray(dataList[c].observation['n'])

            bmean = np.asarray(dataList[c+1].observation['mean'])
            bvar = np.asarray(dataList[c+1].observation['var'])
            bn = np.asarray(dataList[c+1].observation['n'])

            # use indices to ensure data from right depths is used
            ai = 0
            for ad in dataList[c].depth:
                bi = 0
                for bd in dataList[c+1].depth:
                    if ad == bd:
                        # Use scipy.stats.ttest_ind_from_stats.
                        t, p = ttest_ind_from_stats(amean[ai], np.sqrt(avar[ai]), an[ai], bmean[bi], np.sqrt(bvar[bi]),
                                                    bn[bi], equal_var=False)
                        statList.append(["%gcm:"%(ad),t,p])# [depth, t, p]
                    bi = bi + 1
                ai = ai + 1
        else:
            a = dataList[c].observation[~np.isnan(dataList[c].observation)]
            b = dataList[c+1].observation[~np.isnan(dataList[c+1].observation)]
            t, p = ttest_ind(a, b, equal_var=False)
            statList.append(['', t, p])
        # make text with test results
        if mode == 1:
            testresult += "\n\n%s\n%s vs %s" % (dataList[c].site, dataList[c].sitetype, dataList[c + 1].sitetype)
        elif mode == 2:
            testresult += "\n\n%s\n%s vs %s" % (dataList[c].sitetype, dataList[c].site, dataList[c + 1].site)
        for stat in statList:
            testresult += ("\n%s\tt = %.5f  \tp = %.5f \t" % (stat[0], stat[1], stat[2])) + issig(float(stat[2]))
        c += 2
    if printtxt:
        print header, testresult
    if savetxt:
        outFile = os.path.join(savetxt, var.title + '_t-test_' + statModeDict[mode] + '.txt')
        with open(outFile, 'w') as txt:
            txt.write(header + testresult)
        print 'Text-file created: ' + outFile

def ttest_stype(inFile, site, variable, savetxt=None, printtxt=False):
    # get data
    var = Variable(variable)
    # distinguish between variables with depths and no depth. If depth, the values belong to a population of values
    # from the same depth. Eg. natural 10 cm (n=6) should be evaluated against cultural 10 cm. 5 and 10 cm can not be
    # evaluated together as they are not independant samples.
    if var.isdepth == 'yes':
        dataList = getdata(inFile, variable, site, 3, 2)
    else:
        dataList = getdata(inFile, variable, site, 3, 4)
    ttest(dataList, 1, var, savetxt, printtxt)

def ttest_site(inFile, site1, site2, stype, variable, savetxt=None, printtxt=False):
    # get data
    var = Variable(variable)
    siteList = [siteDict[site1], siteDict[site2]]
    stypeList = [typeDict[stype]]
    if var.isdepth == 'yes':
        dataList = extract_from_excel(inFile, var, siteList, stypeList, 2)
    else:
        dataList = extract_from_excel(inFile, var, siteList, stypeList, 4)
    ttest(dataList, 2, var, savetxt, printtxt)
