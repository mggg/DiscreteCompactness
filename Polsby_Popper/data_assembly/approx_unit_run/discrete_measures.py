import math


def discrete_perim_and_area(df_dist, df_units, membership,
                            approx_assignment, prorate=True,
                            pop_field="P0010001"):
    '''
    discrete_perim_and_area returns dictionaries giving
    discrete perimeter and area of a district dataframe,
    df_dist in terms of a unit dataframe, df_units.

    The additional required information is membership,
    a dictionary of dictionaries (see approximate_assignment.py)
    and approx_assignment (see approximate_assignment.py).

    prorate is an option to also report prorated stats
    '''
    # perim and area are dictionaries {district: perim, area}
    perim = {}
    area = {}
    for i, dist in df_dist.iterrows():
        perim[dist["geoid"]] = []
        area[dist["geoid"]] = []
        # dist_units is a dict of all units in the district, and their 
        # percent containment
        dist_units = membership[dist["geoid"]]
        tmp_dperim = 0
        tmp_dpperim = 0
        tmp_dperim_pro = 0
        tmp_dpperim_pro = 0

        tmp_darea = 0
        tmp_dparea = 0
        tmp_darea_pro = 0
        tmp_dparea_pro = 0
        for j, unit in df_units.iterrows():
            pop = int(unit[pop_field])
            perc_in_dist = dist_units[unit["geoid"]]
            if unit["geoid"] in approx_assignment[dist["geoid"]]:
                tmp_darea += 1
                tmp_dparea += pop
                if prorate:
                    tmp_darea_pro += perc_in_dist
                    tmp_dparea_pro += pop*perc_in_dist
                if unit.geometry.intersects(dist.geometry.boundary):
                    tmp_dperim += 1
                    tmp_dpperim += pop
                    if prorate:
                        tmp_dperim_pro += perc_in_dist
                        tmp_dpperim_pro += pop*perc_in_dist
        # save the temporary tallies into the dictionary outputs
        perim[dist["geoid"]] = [tmp_dperim, tmp_dpperim]
        if prorate:
            perim[dist["geoid"]].extend([tmp_dperim_pro, tmp_dpperim_pro])

        area[dist["geoid"]] = [tmp_darea, tmp_dparea]
        if prorate:
            area[dist["geoid"]].extend([tmp_darea_pro, tmp_dparea_pro])
    return (perim, area)


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
            # zone is all the districts whose utm is the one in the loop
            zone = self.gdf.loc[self.gdf['utm'] == utm][['geoid',
                                                         'geometry', 'utm']]
            zone["area"] = zone.geometry.area / 1000**2
            zone["perim"] = zone.geometry.length / 1000
            for i, row in zone.iterrows():
                self.area_dict.update({row["geoid"].iloc[0]: row["area"]})
                self.perim_dict.update({row["geoid"].iloc[0]: row["perim"]})
                