# -*- coding: utf-8 -*-
"""
Docstring
"""

import os
from urllib.request import urlopen
from zipfile import ZipFile

# Data retrieval
def get_and_unzip(url, data_dir="."):
    basename = url.split("/")[-1]
    name_with_path = os.path.join(data_dir, basename)
    if not os.path.exists(name_with_path):
        file_data = urlopen(url)
        data_to_write = file_data.read()
        with open(name_with_path, "wb") as f:
            f.write(data_to_write)

        zip_obj = ZipFile(name_with_path)
        zip_obj.extractall(data_dir)
        del(zip_obj)

"""
# State FIPS codes - specify here your state of interest
FIPS = ["01"]       # Alabama


# Create file path to VTD shapefile if it does not exist
if not os.path.exists(os.path.join(os.getcwd(), 'VTD_SHP')):
    os.makedirs(os.path.join(os.getcwd(),'VTD_SHP'))

# Download VTD shapefiles for each FIPS code specified above
for FIP in FIPS:
    url = "https://www2.census.gov/geo/tiger/TIGER2012/VTD/tl_2012_"+FIP+"_vtd10.zip"
    get_and_unzip(url,"VTD_SHP")
    state_fip = FIP


# Create directory for shapefile of whole country
if not os.path.exists(os.path.join(os.getcwd(), 'CD_SHP')):
    os.makedirs(os.path.join(os.getcwd(),'CD_SHP'))
    
# Grab 113th congressional district TIGER shapefile from census

url_cd = "https://www2.census.gov/geo/tiger/TIGERrd13/CD113/tl_rd13_us_cd113.zip"
get_and_unzip(url_cd, "CD_SHP")
    
# Create the data frames and query out state of interest
df_vtds = gpd.read_file("VTD_SHP")
df_cds = gpd.read_file("CD_SHP")
df_statecds = df_cds.loc[df_cds['STATEFP'] == state_fip]
"""