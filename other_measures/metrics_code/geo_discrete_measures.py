# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 14:15:13 2018

@author: assaf, ruth, katya, zach

Example function calls:
    get_discrete_perim(df_statecds, df_vtds)
    get_discrete_area(df_statecds, df_vtds)

"""
import geopandas as gpd
import pandas as pd
   
# Functions for calculating discrete area and perimeter
 
def get_discrete_area(df_container, df_units):
    """Takes in two dataframes, one of a larger container geometry (i.e., congressional
    district) and one of a smaller unit geometry (i.e., VTDs). This function
    calculates the number of smaller units within the larger geometries and appends these
    in a new column to the larger geometries dataframe."""
    
    disc_area = []                 # create empty list
    for i in range(0,len(df_container)):                    # loop through larger geometries
        count = 0
        for j in range(0,len(df_units)):                    # loop through smaller units
            # df_container is a dataframe, geometry calls its spatial data, and contains 
            # checks containment with other spatial data
            if df_container.iloc[i].geometry.contains(df_units.iloc[j].geometry):
                count += 1
        disc_area.append(count)
    return pd.Series(disc_area)              # returns list of areas as series
        
    
def get_discrete_perim(df_container, df_units):
    """Takes in two dataframes, one of a larger container geometry (i.e., congressional
    district) and one of a smaller unit geometry (i.e., VTDs). This function
    calculates the number of smaller units that intersect the boundaries of the larger 
    geometries and appends these in a new column to the larger geometries dataframe."""
    
    disc_perim = []                # create empty list
    for i in range(0,len(df_container)):                    # loop through larger geometries
        count = 0
        for j in range(0,len(df_units)):                    # loop through smaller units
            # df_container is a dataframe, geometry calls its spatial data, and intersects 
            # checks any overlap with other spatial data
            if df_units.iloc[j].geometry.intersects(df_container.iloc[i].geometry.boundary):
                count += 1
        disc_perim.append(count)
    return pd.Series(disc_perim)               # returns list of areas as series





















