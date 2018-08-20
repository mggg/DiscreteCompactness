# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:24:29 2018

@author: assaf, adriana
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import scipy.stats as stats
import tkinter as tk


class PlotData():
    '''
    This class sets up a single plot in the four-subplot matplotlib window.
    '''
    def __init__(self, coords, namexy):
        self.coords = coords
        self.ax = axarr[coords]  # coords are the subplot coordinates
        self.data = comp_table
        self.xname = namexy[0]
        self.yname = namexy[1]
        self.x = self.data[self.xname]
        self.y = self.data[self.yname]
        self.hilited = "0101"  # Alabama district 1 baby!

        self.refresh()

    # refreshes the plot
    def refresh(self):
        self.ax.clear()
        self.selected = self.ax.plot(0, 0, "o", ms=12,
                                     alpha=1, color="red", visible=False)[0]
        self.multi_selected = self.ax.plot(0, 0, "o", ms=12,
                                           alpha=1, color="aqua", visible=False)[0]
        self.set_plot()
        self.set_lots_hilite(coast_list)
        self.set_hilite(self.hilited)
        self.kendall_tau()

    def set_xname(self, new_name):
        try:
            self.xname = new_name
            self.x = self.data[self.xname]
            self.refresh()
        except KeyError:
            print("I could not find this column name!")

    def set_yname(self, new_name):
        try:
            self.yname = new_name
            self.y = self.data[self.yname]
            self.refresh()
        except KeyError:
            print("I couly not find this column name!")

    def set_hilite(self, geoid):
        index = geoids.index(geoid)
        self.selected.set_visible(True)
        self.selected.set_data([self.x[index]], [self.y[index]])
        self.hilited = geoid

    def set_lots_hilite(self, geoid_list):
        xdat = []
        ydat = []
        for geoid in geoid_list:
            index = geoids.index(geoid)
            xdat.append(self.x[index])
            ydat.append(self.y[index])
        # self.multi_selected.set_data(xdat, ydat)
        # self.multi_selected.set_visible(True)
        self.ax.plot(xdat, ydat, "o", color="cornflowerblue")

    # add some titles and labels to the plot
    def set_plot(self):
        self.ax.plot(self.x, self.y, 'o', picker=10, color='saddlebrown')
        self.ax.set_title("Scatter plot of " + self.xname +
                          " and " + self.yname)
        self.ax.set_xlabel(self.xname)
        self.ax.set_ylabel(self.yname)

    # compute and display Kendall Tau scores
    def kendall_tau(self):
        self.tau, self.p_value = stats.kendalltau(self.x, self.y)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
        self.ax.text(0.05, 0.95, str(self.tau)[:6],
                     transform=axarr[self.coords].transAxes, fontsize=14,
                     verticalalignment='top', bbox=props)


def create_col_name(res="discrete", unit="block groups",
                    val="polsby", thresh="0.5", ranked=True, weighted=False):
    ''' This function takes in human variables and converts them
    to the appropriate column headers in the dataset
    '''
    name = ""
    if ranked:
        name += "rank_"
    if res == "discrete":
        name += "disc_"
        if weighted:
            name += "w_"
        if val == "polsby":
            name += "pp_"
        if val in ["perim", "area"]:
            name += val + "_"
        if unit == "block groups":
            name += "g_"
        if unit == "blocks":
            name += "b_"
        if unit == "tracts":
            name += "t_"
        name += thresh
    if res in ["tiger", "500k", "5m", "20m"]:
        name += "cont_"
        if val == "polsby":
            name += "pp_"
        if val in ["perim", "area"]:
            name += val + "_"
        name += res
    return name


def hilite_plots(event):
    # this code finds the plot in which the user clicks
    mouse = event.mouseevent
    ind = event.ind[0]
    (fx, fy) = f.transFigure.inverted().transform((mouse.x, mouse.y))
    for p in plotlist:
        if p.ax.get_position().contains(fx, fy):
            # if the mouse lies in plot p, then the find the selected geoid
            selected_geoid = geoids[ind]
            # update the other plots with that geoid
            for q in plotlist:
                q.set_hilite(selected_geoid)
    return selected_geoid


# this function is called when a point is clicked
def on_pick(event):
    selected_geoid = hilite_plots(event)
    # x_df is the dataframe I use to plot the district
    map_df = gpd.read_file("../approx_unit_run/districting_plans/" +
                           "cb_2013_us_cd113_500k/" +
                           "cb_2013_us_cd113_500k.shp")
    drawmap(selected_geoid, map_df)
    f.canvas.draw()


def drawmap(geoid, df):
    # create a new figure
    # fig2, ax2 = plt.subplots()
    axarr[1, 1].clear()
    patchdict = {}
    for i, dist in df.iterrows():
        if dist["GEOID"] == geoid:
            # this patch corresponds to the district in question
            special_patch = PolygonPatch(dist.geometry, fc='#ff6a06',
                                         ec='#D3D3D3', alpha=1, zorder=2)
        if dist["GEOID"][:2] == geoid[:2]:  # only add the rest of the state
            # these patches correspond to all other districts
            patch = PolygonPatch(dist.geometry, fc='#D3D3D3',
                                 ec='#D3D3D3', alpha=1, zorder=2)
            patchdict.update({i: patch})
            axarr[1, 1].add_patch(patch)
            axarr[1, 1].axis('scaled')
    axarr[1, 1].add_patch(special_patch)
    axarr[1, 1].axis('scaled')
    axarr[1, 1].set_title("district " + str(int(geoid[2:])) + " in " +
                          fips_dict[geoid[:2]])
    plt.draw()


f, axarr = plt.subplots(2, 2)
plt.subplots_adjust(bottom=0.2)


# create a dictionary of FIPS code : state name for titles
fips = pd.read_csv('../state_fips.txt', sep='\t', lineterminator='\n',
                   dtype={"STATE": str, "FIP": str})
fips_dict = {}

for i, row in fips.iterrows():
    fips_dict.update({row["FIP"]: row["STATE"]})

# zoom_df = pd.read_csv("zoom_table.csv", dtype={"geoid": str})
# big_df = pd.read_csv("big_table.csv", dtype={"geoid": str})
# merge_table = zoom_df.merge(big_df, left_on="geoid", right_on="geoid")
comp_table = pd.read_csv("comp_table.csv", dtype={"geoid": str})
geoids = list(comp_table["geoid"])
coast_list = ['1702', '2403', '1701', '3601', '3403', '5104', '0624', '1223', '2606', '2206', '2202', '2609', '2613', '3627', '5301', '4205', '2505', '0626', '1202', '0903', '3911', '2405', '4506', '0618', '0651', '1000', '4501', '1222', '1212', '2708', '0617', '3608', '3626', '4401', '5111', '5504', '0605', '0620', '2402', '3603', '0612', '0648', '2504', '2507', '3410', '3408', '3703', '2614', '5303', '2612', '3614', '3624', '3621', '0101', '5309', '4101', '3625', '4104', '4709', '1709', '0649', '0652', '5103', '5302', '2508', '0613', '0644', '0633', '2601', '0611', '4105', '5310', '0647', '1214', '2506', '0615', '2203', '3404', '4507', '1227', '5508', '1211', '1208', '1201', '1218', '1225', '1204', '2302', '5307', '3707', '2610', '4827', '4834', '2607', '3604', '2804', '0614', '3402', '1502', '1217', '1216', '5506', '3914', '4814', '1301', '3701', '3623', '2201', '2301', '2401', '1203', '3610', '3909', '3301', '5507', '3602', '4402', '0200', '1219', '2509', '3622', '3616', '1226', '5101', '3406', '4836', '5306', '2602', '5501', '0904', '0902', '2605', '1705', '3605', '1206', '1710', '1801', '4203', '5102', '1213', '1707', '5108', '0602', '3611']

names =[]

# Order is top left, top right, bottom left
# names.append([x, y])
# template exs: rank_disc_w_pp_g_0.1_pro, rank_tiger_perim_b_0.1
names.append(["rank_disc_pp_g_0.5","rank_disc_w_pp_g_0.5"])
names.append(["rank_disc_pp_b_0.5","rank_disc_w_pp_g_0.5"])
names.append(["rank_disc_pp_g_0.5_pro","rank_disc_pp_g_0.5_pro"])

plotlist = []
for i in range(3):
    # initializing the plot classes into a list
    plotlist.append(PlotData((int(i/2), i % 2), names[i]))  # turns 0,1,2 to 00,01,10

f.canvas.mpl_connect('pick_event', on_pick)
plt.suptitle("Comparing Polsby Popper scores across cartographic boundary resolutions (with normalized Kendall tau scores)", fontsize=22)
plt.show()
