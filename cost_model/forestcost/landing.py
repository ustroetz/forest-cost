# Determines landing coordinates on closest road to property

import ogr
from sys import maxint
from math import sqrt


def landing(stand_wkt,roadfn):
    
    #stand centroid
    geom = ogr.CreateGeometryFromWkt(stand_wkt)
    centroid_geom = geom.Centroid()
    centroidLon = centroid_geom.GetX()  # Get X coordinates
    centroidLat = centroid_geom.GetY()  # Get Y cooridnates
    

    
    #find closest point on road to stand
    road_shp = ogr.Open(roadfn)
    lyr = road_shp.GetLayer()
    feat = lyr.GetNextFeature()
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
                landing_coords = nearest_point
        
        elif dist1>dist2:
            cur_dist = dist2
            nearest_point = line.GetPoint(1)
            if cur_dist < min_dist:
                min_dist = cur_dist
                landing_coords = nearest_point
        
        else:
            sys.exit('ERROR: Could not find landing for stand')
    
    landing_coords = landing_coords[:-1]

    return landing_coords
    

