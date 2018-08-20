#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 16:50:29 2018

@author: adrianarogers
"""
import pandas as pd
import geopandas as gpd

df = pd.read_csv("big_table_pro.csv", dtype={"geoid": str})
zoom = pd.read_csv("zoom_table.csv", dtype={"geoid": str})

df = df.merge(zoom, left_on = "geoid", right_on = "geoid")
df = df.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'cont_perim', 'cont_area', 'cont_pp', 'rank_cont_pp', 'state_y'], axis=1)
df = df.rename(columns={'state_x': 'state'})

#print(list(df.columns))

for unit in ['b_', 'g_', 't_']:
    for perc in ['0.1', '0.5']:
        for weight in ['w_', '']:
            df["rank_disc_" + weight + "area_" + unit + perc] = df["disc_" + weight + "area_" + unit + perc].rank(ascending = False)
            df["rank_disc_" + weight + "perim_" + unit + perc] = df["disc_" + weight + "perim_" + unit + perc].rank(ascending = False)

for unit in ['g_', 't_']:
    for perc in ['0.1', '0.5']:
        for weight in ['w_', '']:
            for pro in ['pro_', '']:
                df["rank_" + pro + "disc_" + weight + "area_" + unit + perc] = df[pro + "disc_" + weight + "area_" + unit + perc].rank(ascending = False)
                df["rank_" + pro + "disc_" + weight + "perim_" + unit + perc] = df[pro + "disc_" + weight + "perim_" + unit + perc].rank(ascending = False)

for file in ['tiger', '500k', '20m', '5m']:
    df['rank_cont_area_' + file] = df['cont_area_' + file].rank(ascending = False)
    df['rank_cont_perim_' + file] = df['cont_perim_' + file].rank(ascending = False)

print(list(df.columns))
df.to_csv("./comp_table.csv")      # length 54
print(len(list(df.columns)))


#coast = gpd.GeoDataFrame.from_file("../approx_unit_run/districting_plans/500k_coastal_districts_only.shp")
#coast_geoids = list(coast['GEOID'])
#print(coast_geoids)
#
#with open("coast_geoids.txt", "w") as output:
#    output.write(str(coast_geoids))
