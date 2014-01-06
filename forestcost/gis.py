import gdal, osr, numpy, ogr

# get area of stand in acres
def area(stand_wkt):

    # get area
    geom = ogr.CreateGeometryFromWkt(stand_wkt)
    area = geom.GetArea() # get area in m2
    area = round(area*0.000247105, 4) # convert to acre and round
    return area


# get mean of stand 
def zonal_stats(input_value_raster, standfn, stand_wkt):
    
    # Open data
    raster = gdal.Open(input_value_raster)
    stand = ogr.Open(standfn)
    lyr = stand.GetLayer()

    # get raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    # reproject geometry to same projection as raster
    sourceSR = lyr.GetSpatialRef()
    sourceSR.ImportFromEPSG(3857)
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(32610)

    coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
    geom = ogr.CreateGeometryFromWkt(stand_wkt)
    geom.Transform(coordTrans)

    # Get extent of geometry
    ring = geom.GetGeometryRef(0)
    numpoints = ring.GetPointCount()
    pointsX = []; pointsY = []
    for p in range(numpoints):
            lon, lat, z = ring.GetPoint(p)
            pointsX.append(lon)
            pointsY.append(lat)
    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

    # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((yOrigin - ymax)/pixelWidth)
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

    # create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, gdal.GDT_Byte)
    target_ds.SetGeoTransform((xmin, pixelWidth, 0, ymax, 0, pixelHeight))

    # create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    # read raster as arrays
    banddataraster = raster.GetRasterBand(1)
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)

    # mask zone of raster
    zoneraster = numpy.ma.masked_array(dataraster, numpy.logical_not(datamask))
    
    raster = None
    stand = None

    # calculate mean of zonal raster
    return numpy.mean(zoneraster)

