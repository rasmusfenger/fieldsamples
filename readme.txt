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