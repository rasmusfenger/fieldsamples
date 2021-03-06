# input
inFile = '/Users/rasmus/Google Drive/Phd/Field work 2016/olsen p analysis/olsen_analysis_4.xlsx'
sheet = 'Sheet1'
head = 1
sampleID = 0

########################################################################################################################
import os
import pandas as pd
import numpy as np

# read template
template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Labsheet_template.xlsx')
dfTemplate = pd.read_excel(template, 'template1', header=0, parse_cols='A:A', na_values='none')
aTemplate = dfTemplate.values

# read data file
dfData = pd.read_excel(inFile, sheet, header=head, parse_cols='A:AZ', na_values='none')
aData = dfData.values

# define output
root,ext = os.path.splitext(inFile)
head,tail = os.path.split(root)
outFile = os.path.join(head, tail + '_sorted.xlsx')
c = 1
while os.path.isfile(outFile):
    outFile = os.path.join(head, tail + '_sorted' + str(c) + '.xlsx')
    c = c + 1

# prepare empty array for output
colsOut = aData.shape[1] + 1
aOut = np.zeros(shape=(189, colsOut), dtype=object)

# loop through the 189 sampleID's in template
for num in range(0, 189):
    # prepare empty array for each sample ID
    data = np.empty(shape=(1, colsOut), dtype=object)
    data[0, 0] = aTemplate[num][0]
    for sample in aData:
        if aTemplate[num][0] == sample[sampleID]:
            data = [aTemplate[num][0]]
            for s in sample:
                data.append(s)
        aOut[num] = data

# Check which samples have not been co-registered to sampleID
found = 0
for sample in aData:
    for outsample in aOut:
        if sample[sampleID] == outsample[1]:
            found = found + 1
    if found == 0:
        print 'Could not identify: ' + sample[sampleID]
    found = 0
# Check if there are doublettes
foundList = []
found = 0
for sample in aData:
    for sample2 in aData:
        if sample[sampleID] == sample2[sampleID]:
            found = found + 1
    if found > 1:
        if not [sample[sampleID],found] in foundList:
            foundList.append([sample[sampleID],found])
    found = 0
for f in foundList:
    print 'Sample found ' + str(f[1]) + ' times: ' + f[0]

# add array to dataframe
# prepare columns
colList = ['SampleID']
for col in dfData.columns:
    colList.append(col)
dfOut = pd.DataFrame(data=aOut[0:, 0:], columns=colList)
dfOut.to_excel(outFile, sheet_name=sheet, header=True, index=False)

print 'Excelsheet has been sorted: ' + outFile