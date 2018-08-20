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
    def __init__(self, coords):
        self.coords = coords
        self.ax = axarr[coords]  # coords are the subplot coordinates
        self.data = comp_table
        self.xname = "disc_area_g_0.5" # default x and y
        self.yname = "rank_disc_pp_g_0.5"
        self.x = self.data[self.xname]
        self.y = self.data[self.yname]
        self.hilited = "0101"  # Alabama district 1 baby!

        self.refresh()

    # refreshes the plot
    def refresh(self):
        self.ax.clear()
        self.selected = self.ax.plot(0, 0, "o", ms=12,
                                     alpha=1, color="red", visible=False)[0]
        self.set_plot()
        self.set_hilite(self.hilited)
        self.kendall_tau()

    def set_xname(self, new_name):
        try:
            self.xname = new_name
            self.x = self.data[self.xname]
            self.refresh()
        except:
            print("I could not find this column name!")

    def set_yname(self, new_name):
        self.yname = new_name
        self.y = self.data[self.yname]
        self.refresh()

    def set_hilite(self, geoid):
        index = geoids.index(geoid)
        self.selected.set_visible(True)
        self.selected.set_data([self.x[index]], [self.y[index]])
        self.hilited = geoid

    # add some titles and labels to the plot
    def set_plot(self):
        self.ax.plot(self.x, self.y, 'o', picker=10, color='purple')
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


class ColumnInputs():
    def __init__(self, location, pltnum):
        self.location = location
        self.pltnum = pltnum
        self.ax = plt.axes(location)
        self.butt = plt.Button(self.ax, self.make_name())
        self.butt.on_clicked(self.input_window)
        self.name = ""

    def make_name(self):
        if self.pltnum == 0:
            return "Upper Left"
        if self.pltnum == 1:
            return "Upper Right"
        if self.pltnum == 2:
            return "Bottom Left"

    def input_window(self, event):
        def input_entry_fields_x():
            res = res_x.get()
            val = val_x.get()
            unit = unit_x.get()
            thresh = thresh_x.get()
            rk = ranked_x.get()
            wt = weighted_x.get()
            name = create_col_name(res, unit, val, thresh, rk, wt)
            print(name)
            plotlist[self.pltnum].set_xname(name)
            
        def input_entry_fields_y():
            res = res_y.get()
            val = val_y.get()
            unit = unit_y.get()
            thresh = thresh_y.get()
            rk = ranked_y.get()
            wt = weighted_y.get()
            name = create_col_name(res, unit, val, thresh, rk, wt)
            print(name)
            plotlist[self.pltnum].set_yname(name)

        master = tk.Tk()
        master.title("Set x and y axes")

        mainframe = tk.Frame(master)
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # Dictionary with options
        tk.Label(mainframe, text="SET X PLOT DATA").grid(row=0, column=0)
        
        def deactivate_x(*args):
            if not res_x.get() == "discrete":
                thresh_menu_x.configure(state="disabled")
                unit_menu_x.configure(state="disabled")
                wt_butt_x.configure(state="disabled")
            if res_x.get() == "discrete":
                thresh_menu_x.configure(state="active")
                unit_menu_x.configure(state="active")
                wt_butt_x.configure(state="active")
                
        # discrete vs continuous input
        res_x = tk.StringVar(master)
        choices = {"discrete", "tiger", "500k", "5m", "20m"}
        res_x.set('discrete')  # set the default option
        tk.Label(mainframe, text="Resolution").grid(row=1, column=0)
        res_menu_x = tk.OptionMenu(mainframe, res_x, *choices)
        res_menu_x.grid(row=2, column=0)
        
        res_x.trace("w", deactivate_x)
        
        # unit input (only if res == discrete)
        unit_x = tk.StringVar(master)
        choices = {"blocks", "block groups", "tracts"}
        unit_x.set("block groups")
        tk.Label(mainframe, text="Unit").grid(row=1, column=1)
        unit_menu_x = tk.OptionMenu(mainframe, unit_x, *choices)
        unit_menu_x.grid(row=2, column=1)

        # threshold input (only if res == discrete)
        thresh_x = tk.StringVar(master)
        choices = {"0.1", "0.5"}
        thresh_x.set("0.5")
        tk.Label(mainframe, text="Threshold").grid(row=3, column=1)
        thresh_menu_x = tk.OptionMenu(mainframe, thresh_x, *choices)
        thresh_menu_x.grid(row=4, column=1)

        # value input
        val_x = tk.StringVar(master)
        choices = {"polsby", "perim", "area"}
        val_x.set("polsby")
        tk.Label(mainframe, text="What data?").grid(row=3, column=0)
        val_menu_x = tk.OptionMenu(mainframe, val_x, *choices)
        val_menu_x.grid(row=4, column=0)

        ranked_x = tk.IntVar()
        ranked_butt_x = tk.Checkbutton(mainframe, text="ranked",
                                       variable=ranked_x)
        ranked_butt_x.grid(row=5, column=0)

        # pop weighted and prorate buttons (only if res == discrete)
        weighted_x = tk.IntVar()
        wt_butt_x = tk.Checkbutton(mainframe, text="pop weighted",
                                   variable=weighted_x)
        wt_butt_x.grid(row=5, column=1)
        

        # adding buttons for y axis
        tk.Label(mainframe, text="SET X PLOT DATA").grid(row=0, column=0)
        
        def deactivate_y(*args):
            if not res_y.get() == "discrete":
                thresh_menu_y.configure(state="disabled")
                unit_menu_y.configure(state="disabled")
                wt_butt_y.configure(state="disabled")
            if res_y.get() == "discrete":
                thresh_menu_y.configure(state="active")
                unit_menu_y.configure(state="active")
                wt_butt_y.configure(state="active")
                
        # discrete vs continuous input
        res_y = tk.StringVar(master)
        choices = {"discrete", "tiger", "500k", "5m", "20m"}
        res_y.set('discrete')  # set the default option
        tk.Label(mainframe, text="Resolution").grid(row=1, column=2)
        res_menu_y = tk.OptionMenu(mainframe, res_y, *choices)
        res_menu_y.grid(row=2, column=2)
        
        res_y.trace("w", deactivate_y)
        
        # unit input (only if res == discrete)
        unit_y = tk.StringVar(master)
        choices = {"blocks", "block groups", "tracts"}
        unit_y.set("block groups")
        tk.Label(mainframe, text="Unit").grid(row=1, column=3)
        unit_menu_y = tk.OptionMenu(mainframe, unit_y, *choices)
        unit_menu_y.grid(row=2, column=3)

        # threshold input (only if res == discrete)
        thresh_y = tk.StringVar(master)
        choices = {"0.1", "0.5"}
        thresh_y.set("0.5")
        tk.Label(mainframe, text="Threshold").grid(row=3, column=3)
        thresh_menu_y = tk.OptionMenu(mainframe, thresh_y, *choices)
        thresh_menu_y.grid(row=4, column=3)

        # value input
        val_y = tk.StringVar(master)
        choices = {"polsby", "perim", "area"}
        val_y.set("polsby")
        tk.Label(mainframe, text="What data?").grid(row=3, column=2)
        val_menu_y = tk.OptionMenu(mainframe, val_y, *choices)
        val_menu_y.grid(row=4, column=2)

        ranked_y = tk.IntVar()
        ranked_butt_y = tk.Checkbutton(mainframe, text="ranked",
                                       variable=ranked_y)
        ranked_butt_y.grid(row=5, column=2)

        # pop weighted and prorate buttons (only if res == discrete)
        weighted_y = tk.IntVar()
        wt_butt_y = tk.Checkbutton(mainframe, text="pop weighted",
                                   variable=weighted_y)
        wt_butt_y.grid(row=5, column=3)

        showbuttonx = tk.Button(mainframe, text='Input x name',
                                command=input_entry_fields_x)
        showbuttonx.grid(row=6, column=1, sticky=tk.W, pady=4)

        showbuttony = tk.Button(mainframe, text='Input y name',
                                command=input_entry_fields_y)
        showbuttony.grid(row=6, column=3, sticky=tk.W, pady=4)
        tk.mainloop()


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

in1 = ColumnInputs([0.5, 0.05, 0.1, 0.075], 0)
in2 = ColumnInputs([0.6, 0.05, 0.1, 0.075], 1)
in3 = ColumnInputs([0.7, 0.05, 0.1, 0.075], 2)

plotlist = []
for i in range(3):
    # initializing the plot classes into a list
    plotlist.append(PlotData((int(i/2), i % 2)))  # turns 0,1,2 to 00,01,10

f.canvas.mpl_connect('pick_event', on_pick)
plt.suptitle("Comparing Polsby Popper scores across cartographic boundary resolutions (with normalized Kendall tau scores)", fontsize=22)
plt.show()
