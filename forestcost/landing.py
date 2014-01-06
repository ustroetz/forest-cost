# Determines landing coordinates on closest road to property

import ogr,osr
from sys import maxint
from math import sqrt


def stand(stand_wkt,roadfn):
    
    #stand centroid
    geom = ogr.CreateGeometryFromWkt(stand_wkt)
    centroid_geom = geom.Centroid()
    centroidLon = centroid_geom.GetX()  # Get X coordinates
    centroidLat = centroid_geom.GetY()  # Get Y cooridnates
    
    #find closest point on road to stand
    road_shp = ogr.Open(roadfn)
    road_lyr = road_shp.GetLayer()
    for feat in road_lyr:
        geom = feat.GetGeometryRef()
    
        min_dist = maxint

        for line in geom:
            dist1 = sqrt((centroidLat-line.GetY(0))**2+(centroidLon-line.GetX(0))**2)
            dist2 = sqrt((centroidLat-line.GetY(1))**2+(centroidLon-line.GetX(1))**2)
    
            if dist1<dist2:
                cur_dist = dist1
                nearest_point = line.GetPoint(0)
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    coords_landing_stand = nearest_point
        
            elif dist1>dist2:
                cur_dist = dist2
                nearest_point = line.GetPoint(1)
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    coords_landing_stand = nearest_point
        
            else:
                sys.exit('ERROR: Could not find landing for stand')
    
    coords_landing_stand = coords_landing_stand[:-1]

    return coords_landing_stand
    
def road(roadfn,standfn):
    # create centroid of property
    stand_shp = ogr.Open(standfn)
    stand_lyr = stand_shp.GetLayer()
    allStandsGeom = ogr.Geometry(ogr.wkbPolygon)
    for feat in stand_lyr:
        standGeom = feat.GetGeometryRef()
        for ring in standGeom:
            allStandsGeom.AddGeometry(ring)
        
    property_centroid = allStandsGeom.Centroid()
    
    #find closest point on road to stand
    road_shp = ogr.Open(roadfn)
    road_lyr = road_shp.GetLayer()
    road_lyr.SetAttributeFilter("type = 'existing'")
    for feat in road_lyr:
        geom = feat.GetGeometryRef()
    
        min_dist = maxint

        dist1 = sqrt((property_centroid.GetY()-geom.GetY(0))**2+(property_centroid.GetX()-geom.GetX(0))**2)
        dist2 = sqrt((property_centroid.GetY()-geom.GetY(1))**2+(property_centroid.GetX()-geom.GetX(1))**2)
    
        if dist1<dist2:
            cur_dist = dist1
            nearest_point = geom.GetPoint(0)
            if cur_dist < min_dist:
                min_dist = cur_dist
                coords_landing_road = nearest_point
            else:
                sys.exit()
        
        elif dist1>dist2:
            cur_dist = dist2
            nearest_point = geom.GetPoint(1)
            if cur_dist < min_dist:
                min_dist = cur_dist
                coords_landing_road = nearest_point
            else:
                sys.exit()
        
        else:
            sys.exit('ERROR: Could not find landing for stand')

    # Transform from WGS84 to Web Mercator
    coords_landing_road_geom = ogr.Geometry(type=ogr.wkbPoint)
    coords_landing_road_geom.AddPoint_2D(coords_landing_road[0], coords_landing_road[1])
    inSR = coords_landing_road_geom.GetSpatialReference()
    sourceSR = osr.SpatialReference()
    sourceSR.ImportFromEPSG(3857)  # Web Mercator
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326)  # WGS84
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
    coords_landing_road_geom.Transform(coordTrans)
    
    coords_landing_road = (coords_landing_road_geom.GetX(),coords_landing_road_geom.GetY())
        
    return coords_landing_road

