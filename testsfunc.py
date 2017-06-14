from plotfunctions import *

def runtest(inFile, savefig=False):
    site = 6
    type = 3

    # define output folder
    if savefig:
        c = 1
        savefig = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test', str(c))
        while os.path.isdir(savefig):
            c += 1
            savefig = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test', str(c))
        os.mkdir(savefig)
        print 'figures saved here: ', savefig

    ###################
    # test plotmode 1
    print 'testing plotmode 1'
    plotmode = 1
    # variable 1 - soil moisture is used
    var1 = Variable(1, False, False)
    var2 = None
    plot(inFile, site, type, var1, var2, plotmode, savefig=savefig)

    ###################
    # test plotmode 2
    print 'testing plotmode 2'
    # variable 1 - soil moisture is used
    var1 = Variable(1, False, False)
    var2 = None
    for plotmode in [2, 2.1, 2.2, 2.3]:
        plot(inFile, site, type, var1, var2, plotmode, savefig=savefig)

    ###################
    # test plotmode 3
    print 'testing plotmode 3'
    plotmode = 3
    # variable 1 - NDVI, log transformed
    # variable 2 - Depth integrated P
    var1 = Variable(21, 'log', False)
    var2 = Variable(35, False, 35)
    plot(inFile, site, type, var1, var2, plotmode, reg=True, savefig=savefig)


    ###################
    # test plotmode 4
    print 'testing plotmode 4'
    print 'variables without depth'
    # variable 1 - NDVI, log transformed
    # variable 2 - LAI
    var1 = Variable(21, 'log', False)
    var2 = Variable(22, False, False)
    for plotmode in [4, 4.1, 4.2, 4.3]:
        plot(inFile, site, type, var1, var2, plotmode, reg=True, savefig=savefig)

    print 'variables with depth'
    # variable 1 - soil moisture
    # variable 2 - Depth integrated P
    var1 = Variable(1, False, 15)
    var2 = Variable(35, False, 35)
    for plotmode in [4, 4.1, 4.2, 4.3]:
        plot(inFile, site, type, var1, var2, plotmode, reg=True, savefig=savefig)

    print 'variables with and without depth'
    # variable 1 - NDVI, log transformed
    # variable 2 - Depth integrated P
    var1 = Variable(21, 'log', False)
    var2 = Variable(35, False, 35)
    for plotmode in [4, 4.1, 4.2, 4.3]:
        plot(inFile, site, type, var1, var2, plotmode, reg=True, savefig=savefig)