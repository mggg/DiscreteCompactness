import pandas as pd
'''Takes all of the merged block, block group, and tract files, renames the headings, adds state
abbreviations, and reorders the columns. Creates 2 new csvs, big_table and big_table_pro. 
The first does not have prorated values, the second does. '''

# leading in and changing column names of all 8 files (4 zooms, 2 units)
unit_name = ["tract", "bg"]
files = ["tigerline", "cb500k", "cb5m", "cb20m"]

for shape in files:
    for unit in unit_name:
    
        # create (g) and (t) labels for column names
        if(unit == "tract"):
            u = " (t) "
        if(unit == "bg"):
            u = " (g) "
    
        # read in the tigerline shapefiles (separate for each unit)
        df = pd.read_csv("./tables_merged/" + shape + "_" + unit + ".csv", dtype={"geoid": str})
    
        # change the names of the columns to be dependnet on the unit and the percent
        percent_list = ["0.5", "0.1"]
        for percent in percent_list:
            # using richard's column labels
            df = df.rename(columns={"dpolsby_" + percent: "a/p^2" + u + percent,
                                    "dpolsby_pro_" + percent: "pro_a/p^2" + u + percent,
                                    "dpop_polsby_" + percent: "w_a/p^2" + u + percent,
                                    "dpop_polsby_pro_" + percent: "pro_w_a/p^2" + u + percent,
                                    "rank_dpolsby_" + percent: "rank_a/p^2" + u + percent,
                                    "rank_dpolsby_pro_" + percent: "rank_pro_a/p^2" + u + percent,
                                    "rank_dpop_polsby_" + percent: "rank_w_a/p^2" + u + percent,
                                    "rank_dpop_polsby_pro_" + percent: "rank_pro_w_a/p^2" + u + percent,
                                    'dperim_' + percent: 'perim' + u + percent,
                                    'dpperim_' + percent: 'w_perim' + u + percent,
                                    'dperim_pro_' + percent: 'pro_perim' + u + percent,
                                    'dpperim_pro_' + percent: 'pro_w_perim' + u + percent,
                                    'darea_' + percent: 'area' + u + percent,
                                    'dparea_' + percent: 'w_area' + u + percent,
                                    'darea_pro_' + percent: 'pro_area' + u + percent,
                                    'dparea_pro_' + percent: 'pro_w_area' + u + percent})
    
        # change continuous names, which aren't dependent on percent or unit
        df = df.rename(columns={'carea': 'c_area', 'cperim': 'c_perim',
                                'cpolsby': 'c_a/p^2', 'rank_cpolsby': 'rank_c_a/p^2'})
    
        # save the relabelled files in their respective new csvs
        df.to_csv("./tables_merged/" + shape + "_" + unit + ".csv")    

# read in the tract and block group cvs that were just created (this could be avoided but it's ok)
tract = pd.read_csv("./tables_merged/tigerline_tract.csv", dtype={"geoid": str})
bg = pd.read_csv("./tables_merged/tigerline_bg.csv", dtype={"geoid": str})

# merge tracts to block groups by geoid
tract_bg = tract.merge(bg, left_on = "geoid", right_on = "geoid")

# read in the blocks csv
block = pd.read_csv("./tables_merged/merged_blocks.csv", dtype={"geoid": str})

# create duplicate columns for blocks for the percent, that is perim (b) 0.5 = perim (b) 0.1
# because blocks nest (more or less) in districts
for perc in ["0.1", "0.5"]:
    block['perim (b) ' + perc] = block['perim (b)']
    block['w_perim (b) ' + perc] = block['w_perim (b)']
    block['area (b) ' + perc] = block['area (b)']
    block['w_area (b) ' + perc] = block['w_area (b)']
block = block.drop(['perim (b)', 'w_perim (b)', 'area (b)', 'w_area (b)'], axis=1)

# merge tract_bg combo with blocks and rename some duplicate columns after merge
result = tract_bg.merge(block, left_on = "geoid", right_on = "geoid")
result = result.drop(['Unnamed: 0_x', 'Unnamed: 0.1_x', 'Unnamed: 0_y', 'Unnamed: 0.1_y',
                      'c_area_y', 'c_perim_y', 'c_a/p^2_y', 'rank_c_a/p^2_y'], axis=1)
result = result.rename(columns={'c_area_x': 'c_area', 'c_perim_x': 'c_perim',
                                'c_a/p^2_x': 'c_a/p^2', 'rank_c_a/p^2_x': 'rank_c_a/p^2'})

# the following section reorders the columns and does not compute anything
rank1, rank2, score1, score2, perim1, perim2, area1, area2 = ([] for i in range(8))
rank1p, rank2p, score1p, score2p, perim1p, perim2p, area1p, area2p = ([] for i in range(8))
for perc in ["0.1", "0.5"]:
    for u in [" (b) ", " (g) ", " (t) "]:
        rank1 = rank1 + ['rank_w_a/p^2' + u + perc]
        rank2 = rank2 + ['rank_a/p^2' + u + perc]
        score1 = score1 + ['w_a/p^2' + u + perc]
        score2 = score2 + ['a/p^2' + u + perc]

        if u != " (b) ":
            rank1p = rank1p + ['rank_pro_w_a/p^2' + u + perc]
            rank2p = rank2p + ['rank_pro_a/p^2' + u + perc]
            score1p = score1p + ['pro_w_a/p^2' + u + perc]
            score2p = score2p + ['pro_a/p^2' + u + perc]

for u in [" (b) ", " (g) ", " (t) "]:
    for perc in ["0.1", "0.5"]:
        perim1 = perim1 + ['perim' + u + perc]
        perim2 = perim2 + ['w_perim' + u + perc]
        area1 = area1 + ['area' + u + perc]
        area2 = area2 + ['w_area' + u + perc]

        if u != " (b) ":
            perim1p = perim1p + ['pro_perim' + u + perc]
            perim2p = perim2p + ['pro_w_perim' + u + perc]
            area1p = area1p + ['pro_area' + u + perc]
            area2p = area2p + ['pro_w_area' + u + perc]

# Adding state abbreviations
fips = pd.read_csv('../state_fips.txt', sep='\t', lineterminator='\n', dtype={"STATE": str, "FIP": str})
fips_dict = {}
for i, row in fips.iterrows():
    fips_dict.update({row["FIP"]:row["ABBREVIATION"]})
abbrev = []
for i in result['geoid']:
    abbrev.append(fips_dict[i[:2]])
result['state'] = abbrev

result.sort_values('geoid', inplace=True)
result = result.reset_index(drop=True)

# create two csvs: one with prorated values, one without
result = result.rename(columns={'c_a/p^2': 'c_4pi*a/p^2', 'rank_c_a/p^2': 'rank_c_4pi*a/p^2'})
contin = ['geoid', 'state', 'c_perim', 'c_area', 'c_4pi*a/p^2', 'rank_c_4pi*a/p^2']
result_nopro = result[contin + rank1 + rank2 + score1 + score2 + perim1 + perim2 + area1 + area2]
result_pro = result[contin + rank1 + rank1p + rank2 + rank2p +
                    score1 + score1p + score2 + score2p +
                    perim1 + perim1p + perim2 + perim2p +
                    area1 + area1p + area2 + area2p]

# Write to CSV here to keep old header names
#result_nopro.to_csv("./big_table.csv")      # length 54
#result_pro.to_csv("./big_table_pro.csv")    # length 86 because 54+32 for prorated

# Set new header names
result_nopro.rename(columns=lambda x: x.replace(' (b) ', '_b_'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace(' (g) ', '_g_'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace(' (t) ', '_t_'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('c', 'cont'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('4pi*a/p^2', 'pp'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('w_a/p^2', 'disc_w_pp'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('a/p^2', 'disc_pp'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('area', 'disc_area'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('w_disc_area', 'disc_w_area'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('perim', 'disc_perim'), inplace=True)
result_nopro.rename(columns=lambda x: x.replace('w_disc_perim', 'disc_w_perim'), inplace=True)
result_nopro = result_nopro.rename(columns={'cont_disc_perim': 'cont_perim', 'cont_disc_area': 'cont_area'})

result_pro.rename(columns=lambda x: x.replace(' (b) ', '_b_'), inplace=True)
result_pro.rename(columns=lambda x: x.replace(' (g) ', '_g_'), inplace=True)
result_pro.rename(columns=lambda x: x.replace(' (t) ', '_t_'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('c', 'cont'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('4pi*a/p^2', 'pp'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('w_a/p^2', 'disc_w_pp'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('a/p^2', 'disc_pp'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('area', 'disc_area'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('w_disc_area', 'disc_w_area'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('perim', 'disc_perim'), inplace=True)
result_pro.rename(columns=lambda x: x.replace('w_disc_perim', 'disc_w_perim'), inplace=True)
result_pro = result_pro.rename(columns={'cont_disc_perim': 'cont_perim', 'cont_disc_area': 'cont_area'})



result_nopro.to_csv("./big_table.csv")      # length 54
result_pro.to_csv("./big_table_pro.csv")    # length 86 because 54+32 for prorated

header_nopro = ['', '', 'CONTINUOUS:', 'CONTINUOUS:',  'CONTINUOUS SCORE:', 'CONTINUOUS RANK:', 
           'POP RANK:', 'POP RANK:', 'POP RANK:', 'POP RANK:', 'POP RANK:', 'POP RANK:',
           'RANKING:', 'RANKING:', 'RANKING:', 'RANKING:', 'RANKING:', 'RANKING:',
           'POP SCORE:', 'POP SCORE:', 'POP SCORE:', 'POP SCORE:', 'POP SCORE:', 'POP SCORE:',
           'SCORE:', 'SCORE:', 'SCORE:', 'SCORE:', 'SCORE:', 'SCORE:',
           'PERIM:', 'PERIM:', 'PERIM:', 'PERIM:', 'PERIM:', 'PERIM:',
           'POP PERIM:', 'POP PERIM:', 'POP PERIM:', 'POP PERIM:', 'POP PERIM:', 'POP PERIM:',
           'AREA:', 'AREA:', 'AREA:', 'AREA:', 'AREA:', 'AREA:',
           'POP AREA:', 'POP AREA:', 'POP AREA:', 'POP AREA:', 'POP AREA:', 'POP AREA:']

header_pro = ['', '', 'CONTINUOUS:', 'CONTINUOUS:',  'CONTINUOUS SCORE:', 'CONTINUOUS RANK:', 
           'POP RANK:', 'POP RANK:', 'POP RANK:', 'POP RANK:', 'POP RANK:', 'POP RANK:',
           'PRO POP RANK:', 'PRO POP RANK:', 'PRO POP RANK:', 'PRO POP RANK:', 
           'RANKING:', 'RANKING:', 'RANKING:', 'RANKING:', 'RANKING:', 'RANKING:',
           'PRO RANKING:', 'PRO RANKING:', 'PRO RANKING:', 'PRO RANKING:', 
           'POP SCORE:', 'POP SCORE:', 'POP SCORE:', 'POP SCORE:', 'POP SCORE:', 'POP SCORE:',
           'PRO POP SCORE:', 'PRO POP SCORE:', 'PRO POP SCORE:','PRO POP SCORE:',
           'SCORE:', 'SCORE:', 'SCORE:', 'SCORE:', 'SCORE:', 'SCORE:',
           'PRO SCORE:', 'PRO SCORE:', 'PRO SCORE:', 'PRO SCORE:',
           'PERIM:', 'PERIM:', 'PERIM:', 'PERIM:', 'PERIM:', 'PERIM:',
           'PRO PERIM:', 'PRO PERIM:', 'PRO PERIM:', 'PRO PERIM:', 
           'POP PERIM:', 'POP PERIM:', 'POP PERIM:', 'POP PERIM:', 'POP PERIM:', 'POP PERIM:',
           'PRO POP PERIM:', 'PRO POP PERIM:',  'PRO POP PERIM:', 'PRO POP PERIM:',
           'AREA:', 'AREA:', 'AREA:', 'AREA:', 'AREA:', 'AREA:',
           'PRO AREA:', 'PRO AREA:', 'PRO AREA:', 'PRO AREA:',
           'POP AREA:', 'POP AREA:', 'POP AREA:', 'POP AREA:', 'POP AREA:', 'POP AREA:',
           'PRO POP AREA:', 'PRO POP AREA:', 'PRO POP AREA:', 'PRO POP AREA:']
result_nopro.columns = pd.MultiIndex.from_tuples(list(zip(result_nopro.columns, header_nopro)))
result_pro.columns = pd.MultiIndex.from_tuples(list(zip(result_pro.columns, header_pro)))

result_nopro.to_csv("./stylized/style_big_table.csv")      # length 54
result_pro.to_csv("./stylized/style_big_table_pro.csv")    # length 86 because 54+32 for prorated

# richard's table has 48 columns
# ours (without prorated) has 54 because 48 + 4 for contin + 1 for geoid + 1 for state
