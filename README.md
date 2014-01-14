## Forest Cost


### Overview
The Forest Cost package estimates forest logging roads for a set of timber stands and calcualtes the harvest cost for each stand (stumpage two mill gate).

The Forest Cost package consist of two major modules: 
* [Log Road Model](https://github.com/ustroetz/log-road)
* [Cost Model](https://github.com/ustroetz/cost_model)

Additional information about the two moduls can be found in their individual repositories. 

### Sample Test Run

Input GIS Data
```
    ### GIS Data
    slope_raster = 'testdata/Slope.tif'
    elevation_raster = 'testdata/DEM.tif'
    costSurface = 'testdata/CostSurface.tif'
    standfn = 'testdata/test_stands.shp'    # (in EPSG 3857)
    mill_shp = 'testdata/mills.shp'         # optional, alternativly coordinates of the mill can be provided (in EPSG 3857)
    newRoadsfn = 'testdata/newRoad.shp'     # name of new road shapefile to be created
```
<br/>
Log Road Model runs. It creates the new shapefile, and returns the length (m) and cumulative travel cost of the traversed cells of the costsurface 
```
    # Create new road shapefile
    if os.path.exists(newRoadsfn) is not True:
        length, travelCost = rm.main(standfn,costSurface,newRoadsfn)
```
<br/>
The landing on the existing OSM roads is created. 
```
    # Road Landing Coordinates
    coords_landing_road = landing.road(newRoadsfn,standfn) # ((lon, lat) tuple)
```
<br/>
If a mill shapefile is provided, the closest mill is determined. Else the specified coordinates are used. OSRM routing is used to determine the distance and time from the road landing to the closest mill.
```
    # Routing
    haulDist, haulTime, coord_mill = r.routing(coords_landing_road,mill_coords=None, mill_shp=mill_shp)
```
<br/>
Harvest costs for each stand are determined and returned in a dictionary. Input tree data can be specified for each individual stand (here the same tree data are assumed for each stand.)
```
    stand_shp = ogr.Open(standfn)
    stand_lyr = stand_shp.GetLayer()
    standCount = stand_lyr.GetFeatureCount()
    for stand in stand_lyr:
                
        stand_geom = stand.GetGeometryRef()
        stand_wkt = stand_geom.ExportToWkt()

        area = gis.area(stand_wkt)
        elevation = gis.zonal_stats(elevation_raster, standfn, stand_wkt)
        slope = gis.zonal_stats(slope_raster, standfn, stand_wkt)
        
        coords_landing_stand = landing.stand(stand_wkt,newRoadsfn)        

        ### Tree Data ###
        # Harvest Type (clear cut = 0, partial cut = 1)
        PartialCut = 0
        # Hardwood Fraction
        HdwdFractionCT = 0.15
        HdwdFractionSLT = 0.0
        HdwdFractionLLT = 0.0
        # Chip Trees
        RemovalsCT = 200.0
        TreeVolCT = 5.0
        # Small Log Trees
        RemovalsSLT = 100.00
        TreeVolSLT = 70.0
        # Large Log Trees
        RemovalsLLT = 20.00
        TreeVolLLT = 100.00
        
        cost = m.cost_func(
            # stand info
            area,
            elevation,
            slope,
            stand_wkt,
            # harvest info
            RemovalsCT,
            TreeVolCT,
            RemovalsSLT,
            TreeVolSLT,
            RemovalsLLT,
            TreeVolLLT,
            HdwdFractionCT,
            HdwdFractionSLT,
            HdwdFractionLLT,
            PartialCut,
            # road construction info
            lengthNewRoad, 
            totaltravelCostNewRoad,
            standCount,
            # routing info
            coords_landing_stand,
            coords_landing_road,
            haulDist,
            haulTime,
            coord_mill
            )
        
        pprint(cost)  
