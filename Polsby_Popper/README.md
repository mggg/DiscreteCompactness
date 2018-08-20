# discrete_pipeline
Building the pipeline to harvest discrete compactness measures. To go straight to our results, navigate to tables_and_figures/Tables. 

## data_assembly
Contains the code that did the heavy lifting. It collects data from the Census API and computes discrete measures for census blocks, block groups, and tracts. The directory it split into approx_unit_run/ and discrete_blocks_run/. approx_unit_run/ computes these measures for block groups and tracts and discrete_blocks_run/ does so for blocks. 


Blocks are separated from block groups and tracts in our code because since blocks (in general) nest inside districts, we used block assignment files (from the census) to assign each block to a district. Additionally, we only looked at blocks with respect to the TIGER/Line files. However, with block groups and tracts, we computed the area and perimeter using the TIGER/Line and three cartographic boundary files: cb_2013 for 20m, 500k, and 5m (three levels of "zoom"). 


Despite these differences between blocks and block groups/tracts, both directories, approx_unit_run/ and discrete_blocks_run/ have a get_unit_data.py or get_data.py file which functions in a similar way by making calls to the Census API (must insert your own Census API key to use). These scripts output a states directory which, if ran, would result in close to 40 GB of data. 


Next, create_csv.py takes the data for all 50 states, computes membership/inclusion, if needed, and finds discrete area and perimeter. This script calls approximate_assignment.py and discrete_measures.py. Importantly, in discrete_measures.py, we project each state to its appropriate UTM before calculating area and perimeter. The end result is a separate table for each state, unit, and districting plan. 


Run merge_table.py to merge these from hundreds of tables to one for each districting plan and unit. 

## code_for_metrics
Contains the code to create readable, merged tables from the result of data_assembly. make_comp_table.py, make_table.py, and make_zoom_table.py all do this to make different tables (we hope to combine these). comp_table.csv is one giant table that the interactive tool relies on. 


Run table_analysis.py for an interactive matplotlib and tkinter tool where you can choose which discrete metrics to plot against each other. 

## tables_and_figures
Contains the final versions of three tables: final_big_table.csv, final_big_table_pro.csv, and final_zoom_table.csv. final_big_table.csv and final_big_table_pro.csv only have the results from the TIGER/Line files. The difference between them is that the second has all of the prorated discrete measures as well. final_zoom_table.csv contains all cartographic boundary files.


The naming convention for table headings is as follows: 
* rank: either a ranking of 1 to 435 or raw score, in the case of polsby popper score, rank 1 means highest (best) score
* tiger/500k/5m/20m: these represent the 4 distriting files at different levels of zoom, either the TIGER/Line or the 3 cartographic boundary files. The order from highest resolution to lowest is: 500k, 5m, 20m. 
* w: population weighted
* pp: polsby popper, if cont_pp, calculated as 4*pi*area/perimeter^2. If discrete, calculated as area/perimeter^2
* perim/area: the raw number of discrete units counted along the perimeter or area
* b/g/t: block, group, or tract
* 0.1/0.5: 10% or 50% inclusion counted as being inside the district
* pro: prorated
