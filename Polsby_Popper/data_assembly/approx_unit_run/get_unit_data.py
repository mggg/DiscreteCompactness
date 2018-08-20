#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 18:30:41 2018
@author: hannah
"""
import requests
import pandas as pd
from pprint import pprint
import os

import geopandas as gpd

from urllib.request import urlopen
from zipfile import ZipFile
import time

def dict_invert(dictionary):
  dict = {val: [key for key in dictionary.keys()
          if dictionary[key] == val] for val in dictionary.values()}
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

def get_unit_data(fip, unit_name):
    CENSUS_API_KEY = "YOUR KEY HERE"
    HOST = "https://api.census.gov/data"
    # set year for data and acs5 or sf1 (sf1 stands for summary file 1)
    # as of july, 2018 - documentation can be found here:
    # https://www.socialexplorer.com/data/c2010/metadata/?ds=sf1
    year = "2010"
    dataset = "sf1"
    base_url = "/".join([HOST, year, dataset])
    # the variables we want are name and total population
    get_variables = ["NAME", "P0010001"]

    # list of all county codes in a txt file in this folder
    county_codes = pd.read_csv('full_county_fips_2010.csv',
            header = None,
            names = ["STATE", "STATEFP", "COUNTYFP",
                "COUNTY_NAME", "CLASSFP"],
            dtype = {"STATE":str, "STATEFP":str,
                "COUNTYFP":str, "COUNTY_NAME":str,
                "CLASSFP":str})
            # creates a dictionary {state: list of counties in that state}
    county_state_dictionary = {county_codes.iloc[i]["STATEFP"] +
            county_codes.iloc[i]["COUNTYFP"]:
            county_codes.iloc[i]["STATEFP"]
            for i in range(len(county_codes))}
    state_county_dict = dict_invert(county_state_dictionary)


    print('working on state FIPS: ' + fip)
    if not os.path.exists(os.path.join(os.getcwd(), "states", fip)):
       os.makedirs(os.path.join(os.getcwd(), "states", fip))
    os.chdir("./states/" + fip)
    data = []
    for county_code in state_county_dict[fip]:
        predicates = {}
        predicates["get"] = ",".join(get_variables)
        #### make changes here for tracts
        predicates["for"] = unit_name + ":*"
        #state fips code, here 42 is Pennsylvania
        predicates["in"] = "state:" + fip + "+county:" + county_code[2:]
        predicates["key"] = CENSUS_API_KEY
        #  Write the result to a response object:
        response = requests.get(base_url, params=predicates)
        try:
            print("succeeded to find data for: " + county_code + " :)")
            col_names = response.json()[0]
            data = data + response.json()[1:]
        except:
            print("failed to find data for: " + county_code + " :(")
    geoids = [] #initialize geoid vector
    census_df = pd.DataFrame(columns=col_names, data=data)
    for index, row in census_df.iterrows():
        if unit_name == "tract":
            geoid = row["state"] + row["county"] + row[unit_name]
        else:
            geoid = row["state"] + row["county"] + row["tract"] + row[unit_name]
        geoids.append(geoid)
    census_df["GEOID10"] = geoids
    census_df.set_index(["state", "county", "tract"],
                                  drop=False, inplace=True)
    print("starting to merge " + unit_name)
    t0 = time.time()
    if unit_name == "tract":
       unit_url = "https://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_" + fip + "_tract10.zip"    #2010 tigerline tracts shapefile

    if unit_name == "bg":
       unit_url = "https://www2.census.gov/geo/tiger/TIGER2010/BG/2010/tl_2010_" + fip + "_bg10.zip"             #2010 tigerline block groups shapefile

    #uname is an abbreviation for naming conventions only.
    if unit_name == "block group":
        unit_url = "https://www2.census.gov/geo/tiger/TIGER2010/BG/2010/tl_2010_" + fip + "_bg10.zip"             #2010 tigerline block groups shapefile
        uname = "bg"
    else:
        uname = unit_name
    get_and_unzip(unit_url, os.getcwd())
    shp_unit = gpd.read_file("tl_2010_" + fip + "_" + uname + "10.shp")
    units = pd.merge(shp_unit, census_df, on="GEOID10")
    units.to_file(driver='ESRI Shapefile',
                  filename='2010_' + fip + '_' + uname +'_pop.shp')
    os.remove("tl_2010_" + fip + "_" + uname + "10.zip")
    os.remove("tl_2010_" + fip + "_" + uname + "10.dbf")
    os.remove("tl_2010_" + fip + "_" + uname + "10.prj")
    os.remove("tl_2010_" + fip + "_" + uname + "10.shp")
    os.remove("tl_2010_" + fip + "_" + uname + "10.shp.xml")
    os.remove("tl_2010_" + fip + "_" + uname + "10.shx")
    print("finished " + uname + str(int(time.time()-t0)) + " seconds")

    os.chdir("../..")

states = ['53', '10', '11', '55','54',
          '15', '12', '56', '34', '35',
          '48', '22', '37', '38', '31',
          '47', '36', '42', '02', '32',
          '33', '51', '08', '06', '01',
          '05', '50', '17', '13', '18',
          '19', '25', '04', '16', '09',
          '23', '24', '40', '39', '49',
          '29', '27', '26', '44', '20',
          '30', '28', '45', '21', '41', '46']
states = sorted(states)
for i in states:
    print(os.getcwd())
    # the last input here should be "block group" or "tract"
    get_unit_data(i, "block group")
    print("done fips: "+i)
