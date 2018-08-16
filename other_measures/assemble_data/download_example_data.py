# -*- coding: utf-8 -*-
"""
get_example_data: Module to download shapefiles of Congressional Districts for 
    113th Congress and VTDs from 2012 for a given state. If run as script, will
    download New Hampshire and store in data folder of GitHub repository. 
    Data folder is in .gitignore and will not be stored in the repo. New
    Hampshire is used because it is the smallest file download with more than
    one Congressional District.

"""

import os
import tempfile
from urllib.request import urlopen
from zipfile import ZipFile

# Data retrieval
def get_and_unzip(url, data_dir = os.getcwd()):
    file_data = urlopen(url)
    data_to_write = file_data.read()
    # with open(name_with_path, "wb") as f:
    with tempfile.TemporaryFile() as f:
        f.write(data_to_write)
        zip_obj = ZipFile(f)
        zip_obj.extractall(data_dir)
        del(zip_obj)

def get_example_state(fips, data_dir = os.getcwd()):
    
    basename = "tl_2012_" + str(fips) + "_vtd10"
    if not os.path.exists(os.path.join(data_dir, basename + ".shp")):
        url = "https://www2.census.gov/geo/tiger/TIGER2012/VTD/" + basename + ".zip"
        get_and_unzip(url, data_dir)
    
    basename = "tl_rd13_" + str(fips) + "_cd113"
    if not os.path.exists(os.path.join(data_dir, basename + ".shp")):
        url = "https://www2.census.gov/geo/tiger/TIGERrd13/CD113/" + basename + ".zip"
        get_and_unzip(url, data_dir)

def main():
    data_dir = "../data"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    get_example_state("33", data_dir)
    
if __name__ == "__main__":
    main()
