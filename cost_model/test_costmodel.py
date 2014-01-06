from forestcost import main_model as m
from forestcost import routing as r
from forestcost import landing
from forestcost import gis
from pprint import pprint
import ogr

if __name__ == '__main__':
    ### GIS Data
    slope_raster = 'testdata//Slope.tif'
    elevation_raster = 'testdata//Slope.tif'
    
    standfn = 'testdata/test_stands.shp' # in EPSG 3857
    stand_shp = ogr.Open(standfn)
    stand_lyr = stand_shp.GetLayer()
    
    roadfn = 'testdata/newRoad2.shp' # in EPSG 3857
    
    ### Mill information
    mill_shp = 'testdata/mills.shp'
    #mill_coords = (-122.665014,45.519218)

    # Road Landing Coordinates
    coords_landing_road = landing.road(roadfn,standfn)
    
    # Routing
    haulDist, haulTime, coord_mill = r.routing(coords_landing_road,mill_coords=None, mill_shp=mill_shp)
        
    for stand in stand_lyr:
                
        stand_geom = stand.GetGeometryRef()
        stand_wkt = stand_geom.ExportToWkt()

        area = gis.area(stand_wkt)
        elevation = gis.zonal_stats(elevation_raster, standfn, stand_wkt)
        slope = gis.zonal_stats(slope_raster, standfn, stand_wkt)
        
        # stand landing coords
        coords_landing_stand = landing.stand(stand_wkt,roadfn)        

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
            # routing info
            coords_landing_stand,
            coords_landing_road,
            haulDist,
            haulTime,
            coord_mill
        )
        
        pprint(cost)




