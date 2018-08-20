import math
import pandas as pd
import glob
'''Takes all of the files in ./tables/ and merges them into a csv, removing the headers, the only water districts, and saves new csv'''

unit_name = ["tract", "bg"]
district_files = ["tigerline", "cb500k", "cb5m", "cb20m"]

for unit in unit_name:
    for shape in district_files:
        interesting_files = glob.glob("./tables/" + shape + "*" + unit + ".csv")
        files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
        df = pd.concat(files, ignore_index = True)
        print(df.columns)

        # There are 3 "districts" that are only water, with geoid ending in "ZZ". Removing these
        tf = [not row['geoid'][2:] == 'ZZ' for i, row in df.iterrows()]
        df = df[tf]
        df = df.reset_index(drop=True)

        # Removing DC
        tf_dc = [not row['geoid'][:2] == '11' for i, row in df.iterrows()]
        df = df[tf_dc]
        df = df.reset_index(drop=True)

        # to add continuous polsby popper:
        df["cpolsby"] = (4 * math.pi * df["carea"]) / (df["cperim"] * df["cperim"])
        df["rank_cpolsby"] = df["cpolsby"].rank(ascending = False)

        percent_list = ["0.5", "0.1"]
        for percent in percent_list:
            df["dpolsby_" + percent] = (df["darea_" + percent]) / (df["dperim_" + percent] * df["dperim_" + percent])
            df["dpolsby_pro_" + percent] = (df["darea_pro_" + percent]) / (df["dperim_pro_" + percent] * df["dperim_pro_" + percent])
            df["dpop_polsby_" + percent] = (df["dparea_" + percent]) / (df["dpperim_" + percent] * df["dpperim_" + percent])
            df["dpop_polsby_pro_" + percent] = (df["dparea_pro_" + percent]) / (df["dpperim_pro_" + percent] * df["dpperim_pro_" + percent])

            df["rank_dpolsby_" + percent] = df["dpolsby_" + percent].rank(ascending = False)
            df["rank_dpolsby_pro_" + percent] = df["dpolsby_pro_" + percent].rank(ascending = False)
            df["rank_dpop_polsby_" + percent] = df["dpop_polsby_" + percent].rank(ascending = False)
            df["rank_dpop_polsby_pro_" + percent] = df["dpop_polsby_pro_" + percent].rank(ascending = False)

        #df = df[['geoid', 'carea', 'cpolsbypop', 'dperim_0.5', 'dpperim_0.5', 'dperim_pro_0.5', 'dpperim_pro_0.5', 'darea_0.5', 'dparea_0.5', 'darea_pro_0.5', 'dparea_pro_0.5', 'dperim_0.1', 'dpperim_0.1', 'dperim_pro_0.1', 'dpperim_pro_0.1', 'darea_0.1', 'dparea_0.1', 'darea_pro_0.1', 'dparea_pro_0.1', 'cpolsby', 'dpolsby_0.5', 'dpolsby_01', 'dpolsby_pro_0.5', 'dpolsby_pro_0.1', 'dpop_polsby_0.5', 'dpop_polsby_0.1', 'dpop_polsby_pro_0.5', 'dpop_polsby_pro_0.1']]

        df.to_csv("./tables_merged/" + shape + "_" + unit + ".csv")
        df.to_csv("../analysis/tables_merged/" + shape + "_" + unit + ".csv")


