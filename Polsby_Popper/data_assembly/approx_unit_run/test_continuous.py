#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 21:59:16 2018

@author: adrianarogers
"""
import pandas as pd
import geopandas as gpd
import math

UTMS = ["02", "04", "05", "10", "11", "12", "13", "14",
        "15", "16", "17", "18", "19", "20", "55"]


class ProjectionCalculator:
    """
    Take a dataframe from Shapefile of census cells
    and assign respective UTM zones, and creates an area and
    perim dictionary. All output units are in km^2
    """
    def __init__(self, gdf):
        """
        param gdf: dataframe containing census cells (usually VTDs)
        """
        # initializing local variables
        self.gdf = gdf.copy(deep=True)
        # sometimes dataframes have geoid in upper case
        self.gdf.columns = map(str.lower, self.gdf.columns)
        self.perim_dict = {}
        self.area_dict = {}
        self.find_utms()
        self.calc_continuous()

    def find_utms(self):
        utm_list = []
        """
        Assign appropriate UTM zone for proper projection.
        """
        # Reproject into lat/long after projection for the intersection
        self.gdf = self.gdf.to_crs({'init': 'epsg:4269'})
        for index, dist in self.gdf.iterrows():
            utm = math.floor((dist.geometry.centroid.x+180)*59/354)+1
            utm = str(utm).zfill(2)
            utm_list.append(utm)
        self.gdf['utm'] = utm_list

    def calc_continuous(self):
        """
        Calculate continuous area and perimeters.
        """
        for utm in UTMS:
            my_epsg = '269' + utm  # epsg crs for a particular utm code
            # changing the crs for the whole dataframe:
            self.gdf = self.gdf.to_crs({"init": "epsg:" + my_epsg})
            print(self.gdf.iloc[0]['utm'])
            # zone is all the districts whose utm is the one in the loop
            zone = self.gdf.loc[self.gdf['utm'] == utm][['geoid',
                                                         'geometry', 'utm']]
            
            zone["area"] = zone.geometry.area / 1000**2
            zone["perim"] = zone.geometry.length / 1000
            for i, row in zone.iterrows():
                self.area_dict.update({row["geoid"].iloc[0]: row["area"]})
                self.perim_dict.update({row["geoid"].iloc[0]: row["perim"]})


dist_df = gpd.GeoDataFrame.from_file("./districting_plans/cd2013/tl_rd13_us_cd113.shp")

state = '56'
districts = dist_df
unit = "bg"
plan_name = "tigerline"

data = {}

#initialize_dataframes(state_fips, unit_df, district_df)
os.chdir('./states/'+state)

state_ind = [districts.iloc[i]['STATEFP'] == state
                 for i in range(len(districts))]
state_districts = districts.iloc[state_ind]
if "geoid" not in list(state_districts):
    state_districts["geoid"] = state_districts["GEOID"]
for d_geoid in state_districts["geoid"]:
    data[d_geoid] = []
state_districts = state_districts.to_crs({'init': 'epsg:2163'})

print('running continuous metrics')
proj = ProjectionCalculator(state_districts)
#test_df = proj.gdf
carea = proj.area_dict
cperim = proj.perim_dict

os.chdir("../../")
if not os.path.exists(os.path.join(os.getcwd(),"./tables")):
    os.makedirs(os.path.join(os.getcwd(),"./tables"))
os.chdir("./tables")
#save_d_data(data, name, path)
with open(plan_name + "_" + state + "_" + unit + '.csv', 'w', newline='') as csvfile:
    metric_writer = csv.writer(csvfile, delimiter=',',\
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #metric_writer.writerow(header_list)
    for d_geoid in data.keys():
#        metric_writer.writerow([d_geoid, carea[d_geoid], cperim[d_geoid], *data[d_geoid]])
        metric_writer.writerow([carea[d_geoid], cperim[d_geoid]])