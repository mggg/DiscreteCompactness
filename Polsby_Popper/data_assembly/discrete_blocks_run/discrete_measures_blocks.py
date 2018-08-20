import geopandas as gpd
import pandas as pd
import shapely.wkt
import networkx as nx

#def discrete_perim_and_area(df_dist, df_units, membership, pop_field = "P0010001"):

UTMS = ["02", "04", "05", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "55"]

class ProjectionCalculator:
    """
    Take a dataframe from Shapefile of census cells and assign respective UTM zones
    """
    def __init__(self, gdf):
        """
        param gdf: dataframe containing census cells (usually VTDs)
        """
        self.gdf = gdf
        self.gdf.columns = map(str.lower, self.gdf.columns)
        self.find_utms
        self.calc_continuous
        self.calc_score

    def find_utms(self):
        """
        Assign appropriate UTM zone for proper projection.
        """
        for index in range(0, len(self.gdf)):
            dist = self.gdf.iloc[[index]][['geoid', 'geometry', 'utm']]
            utm = math.floor((self.gdf.iloc[[index]].centroid.x+180)*59/354)+1
            utm = str(utm).zfill(2)
            dist = dist.assign(utm=utm)
            if index == 0:
                dist_utms = dist
            else:
                dist_utms = pd.concat([dist_utms, dist])
        self.gdf['utm'] = dist_utms['utm']

    def calc_continuous(self):
        """
        Calculate continuous area and perimeters.
        """
        for utm in UTMS:
            zone = self.gdf.loc[self.gdf['utm'] == utm][['geoid', 'geometry', 'utm']]
            epsg = int('269' + utm)
            zone_area = zone.to_crs(epsg=epsg).area/1000**2
            zone = zone.assign(area=zone_area.values)
            zone_peri = zone.to_crs(epsg=epsg).length/1000
            zone = zone.assign(perimeter=zone_peri.values)
            if utm == UTMS[0]:
                calc = zone
            else:
                calc = pd.concat([calc, zone])
        self.gdf = pd.merge(self.gdf, calc, how='left', on=['geoid', 'geometry', 'utm'])

    def calc_score(self):
        """
        Calculate Polsby-Popper scores.
        """
        for index in range(0, len(self.gdf)):
            dist = self.gdf.iloc[[index]][['geoid', 'area', 'perimeter']]
            score = 4*math.pi*dist['area']/dist['perimeter']**2
            dist = dist.assign(score=score)
            if index == 0:
                dist_scores = dist
            else:
                dist_scores = pd.concat([dist_scores, dist])
        self.gdf = pd.merge(self.gdf, dist_scores, how='left', on=['geoid', 'area', 'perimeter'])
