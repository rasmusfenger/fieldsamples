import os
import fiona
from fiona import collection
from fiona.crs import from_epsg
import csv
from shapely.geometry import Point, mapping, shape
from plotfunctions import *

epsg_32622 = 'PROJCS["WGS_1984_UTM_Zone_22N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'

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
        prj.write(epsg_32622)
    print 'Shapefile created: ' + outFile


def make_buf(site, outFile=None, buf=0.5):
    dir = os.path.dirname(os.path.abspath(__file__))
    tempFolder = os.path.join(dir, 'temp')

    if not outFile:
        outFile = os.path.join(dir, 'plot_shapes', siteDict[site] + '_plots.shp')

    # first create point shape file from shape - and save it with prj file. Other wise buffer will not work.
    schema = {'geometry': 'Point', 'properties': {'site': 'str',
                                                  'sitetype': 'str',
                                                  'plot': 'int'}}
    pnt = os.path.join(tempFolder, 'pnt_temp.shp')
    with fiona.open(pnt, "w", crs=from_epsg(32622), driver="ESRI Shapefile", schema=schema) as output:
        reader = csv.DictReader(open("plotlocations.csv"), delimiter=',')
        for row in reader:
            if siteDict[site] == row['site']:
                point = Point(float(row['X']), float(row['Y']))
                prop = {'site': str(row['site']), 'sitetype': str(row['sitetype']), 'plot': int(row['plot'])}
                output.write({'geometry': mapping(point), 'properties': prop})
    prjfile = pnt[:-3] + 'prj'
    with open(prjfile, 'w') as prj:
        prj.write(epsg_32622)

    with collection(pnt, 'r') as input:
        schema = input.schema.copy()
        schema['geometry'] = 'Polygon'
        #schema = {'geometry': 'Polygon', 'properties': {'name': 'str'}}
        with collection(outFile, "w", crs=from_epsg(32622), driver="ESRI Shapefile", schema=schema) as output:
            for point in input:
                prop = point['properties']
                output.write({'properties': prop,
                                'geometry': mapping(shape(point['geometry']).buffer(buf))})
    prjfile = outFile[:-3] + 'prj'
    with open(prjfile, 'w') as prj:
        prj.write(epsg_32622)
    # delete temp file, how to remove entire shapefile?
    print 'Shapefile created: ' + outFile

def extract_from_img(plotShape, imgFile, band=1):
    from rasterstats import zonal_stats
    #plotShape = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plot_shapes', siteDict[site] + '_plots.shp')
    stats = zonal_stats(plotShape, imgFile, band=band, all_touched=False, stats=['mean', 'std', 'min', 'max', 'count'])
    print 'Mean:'
    for stat in stats:
        print stat['mean']
    print '\nStd:'
    for stat in stats:
        print stat['std']


