import os

# geospatial
import geopandas as gpd
import pysal as ps
import numpy as np

# visualization
import matplotlib.pyplot as plt

def get_adjacencies(mapfile):
    # Identify the centroids of the file
    map_centroids = mapfile.centroid
    c_x = map_centroids.x
    c_y = map_centroids.y

    # Spatial Weights
    rW = ps.rook_from_shapefile(shp)
    rW[10] # View neighbors for specific row -> note, all weights = 1.0
    rW.neighbors # View all neighbors
    rW.full()[0] # View full contiguity matrix

    # Would be nice to see attributes for neighbors:
    self_and_neighbors = [10]
    self_and_neighbors.extend(rW.neighbors[10])
    mapfile.iloc[self_and_neighbors, :5]

    return rW

def show_map(rW):

    basemap = df_clean_vtd.plot(color = "white", edgecolor = "lightgray")
    county_centroids.plot(ax = basemap, markersize = 1)

    for i, jj in rW.neighbors.items():
        # origin = centroids[k]
        for j in jj:
            segment = county_centroids
            basemap.plot([c_x[i], c_x[j]], [c_y[i], c_y[j]], linestyle = '-', linewidth = 1)


def export_adjacenccies(rW):

    # With useful ID
    rW = ps.rook_from_shapefile(shp, idVariable = "GEOID")
    gal = ps.open("pr_county_geoid.gal", "w")
    gal.write(rW)
    gal.close()


    # Save Spatial Weights file in GAL format
    gal = ps.open("pr_county.gal", "w")
    gal.write(rW)
    gal.close()

# Importing a .shp file
shp = "cb_2017_72_tract_500k/cb_2017_72_tract_500k.shp"
mapfile = gpd.read_file(shp)

rW = get_adjacencies(mapfile)
# show_map(rw)
export_adjacenccies(rW)
