import os
import fiona
from fiona.crs import from_epsg
import csv
from shapely.geometry import Point, mapping
from plotfunctions import *


def data2shape(inFile, sites, variable, outFolder):
    dataList = getdata(inFile, variable, sites, 3)
    var = Variable(variable)
    outFile = os.path.join(outFolder, dataList[0].site + '_' + var.title + '.shp')

    schema = {'geometry': 'Point', 'properties': {'site': 'str',
                                                  'sitetype': 'str',
                                                  'plot': 'int',
                                                  'data': 'float'}}
    with fiona.open(outFile, "w", crs=from_epsg(32622), driver="ESRI Shapefile", schema=schema) as output:
        for data in dataList:
            reader = csv.DictReader(open("plotlocations.csv"), delimiter=',')
            for row in reader:
                if data.site == row['site'] and data.sitetype == row['sitetype'] and data.plot == int(row['plot']):
                    a = data.observation
                    obs = a[~np.isnan(a)].mean()
                    point = Point(float(row['X']), float(row['Y']))
                    prop = {'site': str(row['site']), 'sitetype': str(row['sitetype']), 'plot': int(row['plot']),
                            'data': float(obs)}
                    output.write({'geometry': mapping(point), 'properties': prop})

    prjfile = outFile[:-3] + 'prj'
    with open(prjfile, 'w') as prj:
        prj.write(
            'PROJCS["WGS_1984_UTM_Zone_22N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]')
    print 'Shapefile created: ' + outFile

