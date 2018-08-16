"""
continuous_measures: Functions to calculate compactness measures, and
components of compactness measures, in Euclidean space. Recommended usage

    import continuous_measure as cm

"""

import geopandas as gpd
from math import pi
from discretecompactness.smallest_enclosing_circle import make_circle

def _discrete_perimeter(geo, geo_cell):
    """Not implemented"""
    
    return None

def _continuous_perimeter(geo):
    """returns geo.length"""
    
    return geo.length

def _discrete_area(geo, geo_cell):
    """Not implemented"""
    
    return None

def _continuous_area(geo):
    """returns geo.area"""
    
    return geo.area

def perimeter(geo, geo_cell = None):
    """
    Return perimeters of geometries in GeoSeries as Series of floats.
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
        
    This function calculates continuous or discrete perimeter. 
    
    Continuous (Euclidean) perimeter is calculated if only geo argument is 
    provided. Currently this function just returns GeoSeries.length. 
    Future improvements could include:
        
        * Checking for lat-long coordinate system and performing geodetic
        measurement
        * Determining appropriate local CRS (most likely a State Plane or UTM
        zone) and performing calculation in that CRS.
        
    NOT YET OPERATIONALIZED: Discrete perimeter is calculated if a second
    geographic argument is provided that represents the "cells" or "building 
    blocks" of the first, larger geography.
    """

    if geo_cell == None:
        # Continuous perimeter
        return _continuous_perimeter(geo)
    else:
        return _discrete_perimeter(geo, geo_cell)

def area(geo, geo_cell = None, convex_hull = False):
    """
    Return areas of geometries in GeoSeries as Series of floats.
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
        convex_hull -- Calculate area of convex hull of geo
        
    This function calculates continuous or area. 
    
    Continuous (Euclidean) area is calculated if only geo argument is 
    provided. Currently this function just returns GeoSeries.area. 
    Future improvements could include:
        
        * Checking for lat-long coordinate system and performing geodetic
        measurement
        * Determining appropriate local CRS (most likely a State Plane or UTM
        zone) and performing calculation in that CRS.
        
    NOT YET OPERATIONALIZED: Discrete area is calculated if a second
    geographic argument is provided that represents the "cells" or "building 
    blocks" of the first, larger geography.
    """

    if geo_cell == None:
        # Continuous area
        if convex_hull:
            return _continuous_area(geo.convex_hull)
        else:        
            return _continuous_area(geo)
    else:
        return _discrete_area(geo)
    
def polsby_popper(geo, geo_cell = None):
    """
    Returns Polsby-Popper (1991) compactness of geo as float
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
    """
    
    return 4 * pi * area(geo, geo_cell) / (perimeter(geo, geo_cell) ** 2)

def schwartzberg(geo, geo_cell = None):
    """
    Returns Schwartzberg (1965) compactness of geo as float
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
    """

    return polsby_popper(geo, geo_cell) ** -0.5

def c_hull_ratio(geo):
    
    return area(geo) / area(geo, convex_hull = True)

def reock(geo):
    """
    Returns Reock (1961) compactness of geo as float
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
    """
    
    mbc_area = geo.convex_hull.apply(lambda x: pi * make_circle(list(x.exterior.coords))[2] ** 2)
    return geo.area / mbc_area

