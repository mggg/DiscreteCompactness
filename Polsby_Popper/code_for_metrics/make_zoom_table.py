import geopandas as gpd
import pandas as pd

"""Makes the zoom table comparing the 4 different zoom levels of shapefiles. 
The list of cartographic boundary files from most to least granular is: ["cb500k", "cb5m", "cb20m"]. 
Tigerline and cb500k differ mostly in their treatment of water. 
The output also includes the land area and water area for each shapefile and corresponding rankings"""


# Load in 4 data tables, used tracts but tract = block group for continuous
files = ["tigerline", "cb500k", "cb5m", "cb20m"]
tiger = pd.read_csv("./tables_merged/tigerline_tract.csv", dtype={"geoid": str})
tiger = tiger.rename(columns={'c_area': 'c_area_tiger', 'c_perim': 'c_perim_tiger',
                              'c_a/p^2': 'c_4pi*a/p^2_tiger', 'rank_c_a/p^2': 'rank_c_4pi*a/p^2_tiger'})
cb500 = pd.read_csv("./tables_merged/cb500k_tract.csv", dtype={"geoid": str})
cb500 = cb500.rename(columns={'c_area': 'c_area_500k', 'c_perim': 'c_perim_500k',
                              'c_a/p^2': 'c_4pi*a/p^2_500k', 'rank_c_a/p^2': 'rank_c_4pi*a/p^2_500k'})
cb5 = pd.read_csv("./tables_merged/cb5m_tract.csv", dtype={"geoid": str})
cb5 = cb5.rename(columns={'c_area': 'c_area_5m', 'c_perim': 'c_perim_5m',
                              'c_a/p^2': 'c_4pi*a/p^2_5m', 'rank_c_a/p^2': 'rank_c_4pi*a/p^2_5m'})
cb20 = pd.read_csv("./tables_merged/cb20m_tract.csv", dtype={"geoid": str})
cb20 = cb20.rename(columns={'c_area': 'c_area_20m', 'c_perim': 'c_perim_20m',
                              'c_a/p^2': 'c_4pi*a/p^2_20m', 'rank_c_a/p^2': 'rank_c_4pi*a/p^2_20m'})

# Merge 4 data tables
df = tiger.merge(cb500,left_on = "geoid", right_on = "geoid").merge(
    cb5,left_on = "geoid", right_on = "geoid").merge(
    cb20, left_on = "geoid", right_on = "geoid")

# Adding state abbreviations
fips = pd.read_csv('../state_fips.txt', sep='\t', lineterminator='\n', dtype={"STATE": str, "FIP": str})
fips_dict = {}
for i, row in fips.iterrows():
    fips_dict.update({row["FIP"]:row["ABBREVIATION"]})
abbrev = []
for i in df['geoid']:
    abbrev.append(fips_dict[i[:2]])
df['state'] = abbrev

# Load in 4 district shapefiles and rename aland and awater to be unique to each
tiger_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cd2013/tl_rd13_us_cd113.shp')
tiger_plan = tiger_plan.rename(columns={'ALAND': 'aland_tiger', 'AWATER': 'awater_tiger'})
cb500_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cb_2013_us_cd113_500k/cb_2013_us_cd113_500k.shp')
cb500_plan = cb500_plan.rename(columns={'ALAND': 'aland_500k', 'AWATER': 'awater_500k'})
cb5_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cb_2013_us_cd113_5m/cb_2013_us_cd113_5m.shp')
cb5_plan = cb5_plan.rename(columns={'ALAND': 'aland_5m', 'AWATER': 'awater_5m'})
cb20_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cb_2013_us_cd113_20m/cb_2013_us_cd113_20m.shp')
cb20_plan = cb20_plan.rename(columns={'ALAND': 'aland_20m', 'AWATER': 'awater_20m'})

df.sort_values('geoid', inplace=True)

# Merge 4 shapefiles to the previously merged data table
df = df.merge(tiger_plan, left_on = "geoid", right_on = "GEOID").merge(
        cb500_plan, left_on = "geoid", right_on = "GEOID").merge(
                cb5_plan, left_on = "geoid", right_on = "GEOID").merge(
                        cb20_plan, left_on = "geoid", right_on = "GEOID")

# Add rankings of land and water
rank_land = []
rank_water = []
for i in ["tiger", "500k", "5m", "20m"]:
    df["rank_aland_" + i] = df["aland_" + i].rank(ascending = False)
    df["rank_awater_" + i] = df["awater_" + i].rank(ascending = False)
    rank_land = rank_land + ['rank_aland_' + i]
    rank_water = rank_water + ['rank_awater_' + i]

# Reoder the columns
df = df[['geoid', 'state', 
         'rank_c_4pi*a/p^2_tiger', 'rank_c_4pi*a/p^2_500k', 'rank_c_4pi*a/p^2_5m', 'rank_c_4pi*a/p^2_20m',
         'c_4pi*a/p^2_tiger', 'c_4pi*a/p^2_500k', 'c_4pi*a/p^2_5m', 'c_4pi*a/p^2_20m',
         'c_perim_tiger', 'c_perim_500k', 'c_perim_5m', 'c_perim_20m',
         'c_area_tiger', 'c_area_500k', 'c_area_5m', 'c_area_20m'] + rank_land + rank_water + [
         'aland_tiger', 'awater_tiger',
         'aland_500k', 'awater_500k',
         'aland_5m', 'awater_5m',
         'aland_20m', 'awater_20m']]

df.rename(columns=lambda x: x.replace('c_', 'cont_'), inplace=True)
df.rename(columns=lambda x: x.replace('4pi*a/p^2', 'pp'), inplace=True)
print(list(df.columns))

# Write new table to CSV
df.to_csv("./zoom_table.csv")  

header = ['', '', 'CONTIN RANK:', 'CONTIN RANK:', 'CONTIN RANK:', 'CONTIN RANK:',
           'CONTIN SCORE:', 'CONTIN SCORE:', 'CONTIN SCORE:', 'CONTIN SCORE:', 
           'CONTIN PERIM:', 'CONTIN PERIM:', 'CONTIN PERIM:', 'CONTIN PERIM:', 
           'CONTIN AREA:', 'CONTIN AREA:', 'CONTIN AREA:', 'CONTIN AREA:', 
           'RANK LAND:', 'RANK LAND:', 'RANK LAND:', 'RANK LAND:',
           'RANK WATER:', 'RANK WATER:', 'RANK WATER:', 'RANK WATER:',
           'LAND', 'WATER', 'LAND', 'WATER', 'LAND', 'WATER', 'LAND', 'WATER']
df.columns = pd.MultiIndex.from_tuples(list(zip(header, df.columns)))

df.to_csv("./stylized/style_zoom_table.csv")

