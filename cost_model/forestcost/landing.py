# Determines landing coordinates on closest road to property

import requests
import json
import ogr
import osr
import os
import tempfile
ogr.UseExceptions()


def landing(shpfn=None, centroid_coords=None):
    if centroid_coords is None:
        
        stand_shp = ogr.Open(shpfn)
        lyr = stand_shp.GetLayer()
        numFeatures = lyr.GetFeatureCount()
        FID = 0
        centroidLonList = []
        centroidLatList = []

        # get centroids of stands
        while FID < numFeatures:
            feat = lyr.GetFeature(FID)
            geom = feat.GetGeometryRef()

            # Transform from Web Mercator to WGS84
            sourceSR = lyr.GetSpatialRef()
            targetSR = osr.SpatialReference()
            targetSR.ImportFromEPSG(4326)  # WGS84
            coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
            geom.Transform(coordTrans)

            # Create centroid of harvest area
            centroid_geom = geom.Centroid()
            centroidLon = centroid_geom.GetX()  # Get X coordinates
            centroidLat = centroid_geom.GetY()  # Get Y cooridnates
            centroidLonList.append(centroidLon)
            centroidLatList.append(centroidLat)
            FID += 1

        # calcualte centroid of all stands
        centroidLon = sum(centroidLonList)/numFeatures
        centroidLat = sum(centroidLatList)/numFeatures
    else:
        centroidLon = centroid_coords[0]
        centroidLat = centroid_coords[1]

    # get nearest point on road from centroid as json string
    headers = {'User-Agent': 'Forestry Scenario Planner'}
    url = "http://router.project-osrm.org/nearest?loc=%f,%f" % (centroidLat, centroidLon)
    tmp = tempfile.gettempdir()
    key = os.path.join(tmp, "%s_%s-None.cache" % (centroidLat, centroidLon))
    if os.path.exists(key):
        # READING FROM CACHE
        with open(key, 'r') as cache:
            data = json.loads(cache.read())
    else:
        response = requests.get(url, headers=headers)
        binary = response.content
        data = json.loads(binary)
        # WRITING TO CACHE
        with open(key, 'w') as cache:
            cache.write(json.dumps(data))

    # parse json string for landing coordinate
    landing_lat, landing_lon = data['mapped_coordinate']

    return (landing_lon, landing_lat)
