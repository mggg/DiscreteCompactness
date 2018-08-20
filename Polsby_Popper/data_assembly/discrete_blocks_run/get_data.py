#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 18:30:41 2018
@author: ASBN
"""

import requests
import pandas as pd
import os

import geopandas as gpd

from urllib.request import urlopen
from zipfile import ZipFile
import time


def dict_invert(dictionary):
    dict = {val: [key for key in dictionary.keys() if dictionary[key] == val]
            for val in dictionary.values()}
    return dict


# Data retrieval
def get_and_unzip(url, data_dir=os.getcwd()):
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


def get_block_data(fip):
    CENSUS_API_KEY = "0df349d964b97ecb10362e8421c616c5fa38f462"
    HOST = "https://api.census.gov/data"
    # set year for data and acs5 or sf1 (sf1 stands for summary file 1)
    # as of July, 2018 - documentation can be found
    # here: https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1
    year = "2010"
    dataset = "sf1"
    base_url = "/".join([HOST, year, dataset])
    # The variables we want are NAME and total population
    get_variables = ["NAME", "P0010001"]
    # List of all county codes in a txt file in this folder
    county_codes = pd.read_csv('full_county_fips_2010.csv',
                               header=None,
                               names=["STATE", "STATEFP", "COUNTYFP",
                                      "COUNTY_NAME", "CLASSFP"],
                               dtype={"STATE": str, "STATEFP": str,
                                      "COUNTYFP": str, "COUNTY_NAME": str,
                                      "CLASSFP": str})
    # creates a dictionary {state: list of counties in that state}
    county_state_dictionary = {county_codes.iloc[i]["STATEFP"] +
                               county_codes.iloc[i]["COUNTYFP"]:
                                   county_codes.iloc[i]["STATEFP"]
                                   for i in range(len(county_codes))}
    state_county_dict = dict_invert(county_state_dictionary)
    if not os.path.exists(os.path.join(os.getcwd(), "states/"+ fip)):
        os.makedirs(os.path.join(os.getcwd(), "states/" + fip))
    os.chdir("./states/" + fip)

    data = []
    for county_code in state_county_dict[fip]:
        predicates = {}
        predicates["get"] = ",".join(get_variables)
        predicates["for"] = "block:*"
        predicates["in"] = "state:" + fip + "+county:" + county_code[2:]
        predicates["key"] = CENSUS_API_KEY
        # Write the result to a response object:
        response = requests.get(base_url, params=predicates)
        col_names = response.json()[0]
        data = data + response.json()[1:]
        print("found data for: " + county_code + "!")
    geoids = []  # initialize geoid vector
    pop_blocks = pd.DataFrame(columns=col_names, data=data)
    for index, row in pop_blocks.iterrows():
        # make changes here for tracts
        geoid = row["state"] + row["county"] + row["tract"] + row["block"]
        geoids.append(geoid)
    pop_blocks = pd.DataFrame(columns=col_names, data=data)
    pop_blocks["GEOID10"] = geoids
    pop_blocks.set_index(["state", "county", "tract"],
                         drop=False, inplace=True)

    print("starting blocks")
    t0 = time.time()
    url_block = "https://www2.census.gov/geo/tiger/" \
                "TIGER2010/TABBLOCK/2010/tl_2010_" + fip + "_tabblock10.zip"
    get_and_unzip(url_block, os.getcwd())
    shp_blocks = gpd.read_file("tl_2010_" + fip + "_tabblock10.shp")
    blocks = pd.merge(shp_blocks, pop_blocks, on="GEOID10")
    blocks.to_file(driver='ESRI Shapefile',
                   filename='2010_' + fip + '_block_pop.shp')
    os.remove("tl_2010_" + fip + "_tabblock10.zip")
    os.remove("tl_2010_" + fip + "_tabblock10.dbf")
    os.remove("tl_2010_" + fip + "_tabblock10.prj")
    os.remove("tl_2010_" + fip + "_tabblock10.shp.xml")
    os.remove("tl_2010_" + fip + "_tabblock10.shp")
    os.remove("tl_2010_" + fip + "_tabblock10.shx")

    print("finished blocks" + str(int(time.time()-t0)) + " seconds")

    os.chdir("../..")

states1 = ['53', '10', '11', '55','54','15',
    '12', '56', '34', '35', '48', '22',
    '37', '38', '31', '47', '36', '42',
    '02', '32', '33', '51', '08', '06']

states2 = ['01', '05', '50', '17', '13', '18',
    '19', '25', '04', '16', '09', '23',
    '24', '40', '39', '49', '29', '27',
    '26', '44', '20', '30', '28', '45',
    '21', '41', '46']
for i in states1:
    print(os.getcwd())
    get_block_data(i)
