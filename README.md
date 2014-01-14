## Forest Cost


### Overview
The Forest Cost package estimates forest logging roads for a set of timber stands and calcualtes the harvest cost for each stand (stumpage two mill gate).

The Forest Cost package consist of two major modules: 
* [Log Road Model](https://github.com/ustroetz/log-road)
* [Cost Model](https://github.com/ustroetz/cost_model)

Additional information about the two moduls can be found in their individual repositories. 

### Sample Test Run

##### Input GIS Data
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
##### Creating the logging roads
Log Road Model runs. It creates the new shapefile, and returns the length (m) and cumulative travel cost of the traversed cells of the costsurface 
```
    # Create new road shapefile
    if os.path.exists(newRoadsfn) is not True:
        length, travelCost = rm.main(standfn,costSurface,newRoadsfn)
```
<br/>
##### Finding the road landing
The landing on the existing OSM roads is created. 
```
    # Road Landing Coordinates
    coords_landing_road = landing.road(newRoadsfn,standfn) # ((lon, lat) tuple)
```
<br/>
##### Routing
If a mill shapefile is provided, the closest mill is determined. Else the specified coordinates are used. OSRM routing is used to determine the distance and time from the road landing to the closest mill.
```
    # Routing
    haulDist, haulTime, coord_mill = r.routing(coords_landing_road,mill_coords=None, mill_shp=mill_shp)
```
<br/>
##### Cost Calculation
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
            area,                           # Stand area (acres)
            elevation,                      # Elevation (ft)
            slope,                          # Slope (%)
            stand_wkt,                      # Well-Known Text geometry of stand polygon

            # harvest info
            RemovalsCT,                     # Chip trees removed (trees per acre)
            TreeVolCT,                      # Chip tree average volume (cubic feet)
            RemovalsSLT,                    # Small log trees removed (trees per acre)
            TreeVolSLT,                     # Small log average volume (cubic feet) 
            RemovalsLLT,                    # Large log trees removed (trees per acre)
            TreeVolLLT,                     # Large log average volume (cubic feet)
            HdwdFractionCT,                 # Proportion of hardwood chip trees (volume of hardwood divided by total volume)
            HdwdFractionSLT,                # Proportion of hardwood small log trees (volume of hardwood divided by total volume)
            HdwdFractionLLT,                # Proportion of hardwood large log trees (volume of hardwood divided by total volume)
            PartialCut,                     # Regen/Clearcut = 0, Thin = 1

            # routing info
            landing_coords,                 # coordinate of landing ((lon, lat) tuple)
            haulDist,                       # distance to mill (miles)
            haulTime,                       # transit time to mill (minutes)
            coord_mill                      # coordinate of mill ((lon, lat) tuple) 
            
            # optional parameters
            NoHelicopter = False,            # if True, Helicopter logging will not be used (default False)
            NoHaulProportion = 1,            # 1 = everything will be hauled, 0 = nothing will be hauled (default 1)
            roadConstructionCostPerFoot = 0  # Cost ($ US/ft) for road construction, gets multiplied with length (based on created road shapefile) (default 0)
            roadConstructionCostPerUnit = 0  # Cost ($ US) for road construction, gets multiplied with accumulative costs of traversed cells on the cost surface  (default 0)
            )
        
        pprint(cost)  
