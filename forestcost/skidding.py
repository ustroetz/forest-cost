import ogr
import osr
ogr.UseExceptions()


def skidding(stand_wkt, landing_coords):

    # create landing geometry
    landing_geom = ogr.Geometry(ogr.wkbPoint)
    landing_geom.AddPoint_2D(landing_coords[0],landing_coords[1])

    # Create centroid of harvest area
    # TODO get point on surface instead of centroid, no direct API for this
    # see http://darrencope.com/2013/11/09/creating-points-on-a-surface-using-ogr/
    stand_geom = ogr.CreateGeometryFromWkt(stand_wkt)
    centroid_geom = stand_geom.Centroid()

    # Create skidding line
    skidLine = ogr.Geometry(type=ogr.wkbLineString)
    skidLine.AddPoint_2D(centroid_geom.GetX(), centroid_geom.GetY())
    skidLine.AddPoint_2D(landing_geom.GetX(), landing_geom.GetY())

    skid_dist = centroid_geom.Distance(landing_geom)
    skid_dist = round((skid_dist)*3.28084, 2)  # convert to feet
    
    # Transform from WGS84 to Web Mercator
    inSR = landing_geom.GetSpatialReference()
    if inSR is None:
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(3857)  # Web Mercator
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326)  # WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        landing_geom.Transform(coordTrans)

    # Create coordinate stand landing tuple
    landing_lat, landing_lon = landing_geom.GetX(), landing_geom.GetY()
    coord_landing_stand = (landing_lat, landing_lon)
    coord_landing_stand_tuple = tuple(coord_landing_stand)
    
    return skid_dist, coord_landing_stand_tuple
