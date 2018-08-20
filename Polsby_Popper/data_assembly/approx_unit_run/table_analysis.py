# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:24:29 2018

@author: assaf, adriana
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from descartes import PolygonPatch

# create a dictionary of FIPS code : state name for titles
fips = pd.read_csv('../state_fips.txt', sep='\t', lineterminator='\n',
                   dtype={"STATE": str, "FIP": str})
fips_dict = {}
for i, row in fips.iterrows():
    fips_dict.update({row["FIP"]: row["STATE"]})


def different_table_plot(xtable_name, ytable_name, xvec, yvec):

    # read and merge relevant dataframes
    df1 = pd.read_csv("./tables_merged/" + xtable_name, dtype={"geoid": str})
    df2 = pd.read_csv("./tables_merged/" + ytable_name, dtype={"geoid": str})

    xdf = df1["geoid"].to_frame()
    xdf["xname"] = df1[xvec]

    ydf = df2["geoid"].to_frame()
    ydf["yname"] = df2[yvec]

    mergedf = xdf.merge(ydf, left_on="geoid", right_on="geoid")

    # the order of these lists is important.
    x = mergedf["xname"]
    y = mergedf["yname"]
    geoids = mergedf["geoid"]
    return (x, y, geoids)


# this function is called when a point is clicked
def on_pick(event):
    # TODO: learn how this code works
    pt = event.artist
    xdata = pt.get_xdata()
    ydata = pt.get_ydata()
    ind = event.ind
    # by trial and error I figured out that this
    # gives a list of selected geoids
    selected_geoid = geoids[ind[0]]
    # print the geoid selected
    print(geoids[ind[0]])
    # selected keeps track of selected points. starts off as invisible
    selected1.set_visible(True)
    selected1.set_data([xdata[ind]], [ydata[ind]])
    # x_df is the dataframe I use to plot the district
    x_df = gpd.read_file("./districting_plans/cb_2013_us_cd113_500k/" +
                         "cb_2013_us_cd113_500k.shp")
    if selected_geoid:
        if selected_geoid[2:] == "ZZ":
            print("district made of water :o")
        else:
            # draws the map that happens when you click a point
            drawmap(selected_geoid, x_df)
    f.canvas.draw()


def drawmap(geoid, df):
    # create a new figure
    # fig2, ax2 = plt.subplots()
    ax4.clear()
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
            ax4.add_patch(patch)
            ax4.axis('scaled')
    ax4.add_patch(special_patch)
    ax4.axis('scaled')
    ax4.set_title("district " + str(int(geoid[2:])) + " in " +
              fips_dict[geoid[:2]])
    plt.draw()


# xvec is the vector along the x-axis for the plot. The name should be
# chosen from one of the headers of xtable_name
xvec = "rank_dpolsby_0.1"
yvec = "rank_dpolsby_0.1"
xtable_name = "tigerline_tract.csv"
ytable_name = "tigerline_bg.csv"

(x, y, geoids) = different_table_plot(xtable_name, ytable_name,
                                      xvec, yvec)

# row and column sharing
f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

selected1 = ax1.plot(0, 0, 'o', ms=12, alpha=1, color='yellow', visible=False)[0]

ax1.plot(x, y, 'o', picker=10)  # larger picker = easier to select point
ax1.set_title("Scatter plot of " + xvec + " and " + yvec)
ax1.set_ylabel(ytable_name + " : " + yvec)
ax1.set_xlabel(xtable_name + " : " + xvec)

ax1.plot(x, y, 'o', picker=10)  # larger picker = easier to select point
ax1.set_title("Scatter plot of " + xvec + " and " + yvec)
ax1.set_ylabel(ytable_name + " : " + yvec)
ax1.set_xlabel(xtable_name + " : " + xvec)

ax1.plot(x, y, 'o', picker=10)  # larger picker = easier to select point
ax1.set_title("Scatter plot of " + xvec + " and " + yvec)
ax1.set_ylabel(ytable_name + " : " + yvec)
ax1.set_xlabel(xtable_name + " : " + xvec)

f.canvas.mpl_connect('pick_event', on_pick)

'''
fig, ax = plt.subplots()
selected = ax.plot(0, 0, 'o', ms=12, alpha=1, color='yellow', visible=False)[0]

ax.plot(x, y, 'o', picker=10)  # larger picker = easier to select point
plt.title("Scatter plot of " + xvec + " and " + yvec)
plt.ylabel(ytable_name + " : " + yvec)
plt.xlabel(xtable_name + " : " + xvec)
fig.canvas.mpl_connect('pick_event', on_pick)
plt.show()
'''