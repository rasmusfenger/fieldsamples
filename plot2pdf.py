from loaddata import *

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

#------------------
def plot2pdf2(variables, plotmode, inFolder, outFilename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch, cm
    from reportlab.lib.pagesizes import letter, landscape

    figlocList = [[15.3, 23.5], [11.7, 23.5], [8.1, 23.5], [4.5, 23.5], [0.9, 23.5]]
    titleloc = 27.5
    c = canvas.Canvas(outFilename)  # , pagesize=landscape(letter))

    for variable in variables:
        var = Variable(variable)
        inFileList = []
        for num in range(1, 6):
            inFile = os.path.join(inFolder, 'plotmode_' + str(plotmode), var.title + ' ' + siteDict[num] + '.png')
            if os.path.isfile(inFile):
                inFileList.append(inFile)
            else:
                print 'figure does not exist: ' + inFile
        if len(inFileList) > 0:
            figsizex = 4
            figsizey = 4
            for num in range(0, len(inFileList)):
                c.drawImage(inFileList[num], figlocList[num][0] * cm, figlocList[num][1] * cm, figsizex * cm, figsizey * cm)
            c.setFont('Helvetica', 8)
            c.drawString(0.5*cm, titleloc*cm, var.title)
        for num in range(0,len(figlocList)):
            figlocList[num][1] = figlocList[num][1] - 4.5
        titleloc -= 4.5
    c.showPage()
    c.save()
    print 'PDF-file created: ' + outFilename
    #else:
    #    print 'Could not create PDF-file - figures not available'

def plot2pdf_allsites2(variables, plotmode, inFolder, outFilename):
    for variable in variables:
        var = Variable(variable)
    inFileList = []
    for num in range(1, 6):
        inFile = os.path.join(inFolder, 'plotmode_' + str(plotmode), var.title + ' ' + siteDict[num] + '.png')
        if os.path.isfile(inFile):
            inFileList.append(inFile)
        else:
            print 'figure does not exist: ' + inFile
    plot2pdf2(inFileList, outFilename, variables)