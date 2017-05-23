# input
inFile = '/Users/rasmus/Google Drive/Phd/Field work 2016/Lab_sheet_v9.35.xlsx'
variable = 34

########################################################################################################################
from plotfunctions import *

# read template
template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Labsheet_template.xlsx')
dfTemplate = pd.read_excel(template, 'template2', header=0, parse_cols='A:C', na_values='none')
aTemplate = dfTemplate.values

# define output file. If file exists a number is added to te end of filename.
root, ext = os.path.splitext(inFile)
head, tail = os.path.split(root)
outFile = os.path.join(head, tail + '_depthintegrated.xlsx')
c = 1
while os.path.isfile(outFile):
    outFile = os.path.join(head, tail + '_depthintegrated' + str(c) + '.xlsx')
    c = c + 1

# prepare empty array for output (60 rows and 1 column more than in template to which data is added later
colsOut = aTemplate.shape[1] + 1
aOut = np.zeros(shape=(60, colsOut), dtype=object)

# Dictionaries for multiplications
didict = {5: 7.5,
          10: 7.5,
          20: 10,
          30: 10}

disanddict = {5: 12.5,
              20: 12.5,
              30: 10}

# read data
dataList = getdata(inFile, variable, 6, 3, plotmode=0)
# loop thorugh data
for data in dataList:
    dint = 0
    for num in range(0, len(data.depth)):
        depth = data.depth[num]
        if np.isnan(data.observation[num]):
            observation = 0
        else:
            observation = data.observation[num]
        if data.site != 'Sandnes': # special case for Sandnes
            dint += observation * didict[depth]
        else:
            dint += observation * disanddict[depth]

        # loop thorugh template and append data to outarray
        for num in range(0, 60):
            if aTemplate[num][0] == data.site and aTemplate[num][1] == data.sitetype and aTemplate[num][2] == data.plot:
                aOut[num][0] = data.site
                aOut[num][1] = data.sitetype
                aOut[num][2] = data.plot
                aOut[num][3] = dint

# add array to dataframe
# prepare columns
colList = []
for col in dfTemplate.columns:
    colList.append(col)
var = Variable(variable)
colList.append(var.title)
dfOut = pd.DataFrame(data=aOut[0:, 0:], columns=colList)
dfOut.to_excel(outFile, sheet_name='Sheet1', header=True, index=False)

print 'Depth integration calculated: ' + outFile