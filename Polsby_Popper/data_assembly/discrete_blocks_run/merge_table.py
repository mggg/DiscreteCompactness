import pandas as pd
import glob
'''Takes all of the files in ./tables/ and merges them into a csv, removing the headers, and saves new csv'''

interesting_files = glob.glob("./tables/*.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)

# There are 3 "districts" that are only water, with geoid ending in "ZZ". Removing these
tf = [not row['geoid'][2:] == 'ZZ' for i, row in df.iterrows()]
df = df[tf]
df = df.reset_index(drop=True)

# Removing DC
tf_dc = [not row['geoid'][:2] == '11' for i, row in df.iterrows()]
df = df[tf_dc]
df = df.reset_index(drop=True)

percent_list = ["0.5", "0.1"]

for perc in percent_list:
    df["a/p^2 (b) " + perc] = (df["darea"]) / (df["dperim"] * df["dperim"])
    df["w_a/p^2 (b) " + perc] = (df["dparea"]) / (df["dpperim"] * df["dpperim"])
    df["rank_a/p^2 (b) " + perc] = df["a/p^2 (b) " + perc].rank(ascending = False)
    df["rank_w_a/p^2 (b) " + perc] = df["w_a/p^2 (b) " + perc].rank(ascending = False)

df = df.rename(columns={'dperim': 'perim (b)', 'dpperim': 'w_perim (b)', 
                        'darea': 'area (b)', 'dparea': 'w_area (b)'})

print(len(df))
df.to_csv("merged_blocks.csv")
df.to_csv("../analysis/tables_merged/merged_blocks.csv")


