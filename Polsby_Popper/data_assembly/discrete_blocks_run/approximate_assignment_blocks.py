#import math
import geopandas as gpd
import shapely.wkt
import networkx as nx
import pysal


def networkx_from_matrix_and_list(adj, names):
    G = nx.from_numpy_matrix(adj)
    G.relabel_nodes(G,{ind:names(ind) for ind in range(len(names))})
    return G

def make_adj_graph(units, membership, inclusion_percent):
    '''
    units: geodataframe of units
    membership: see above functions
    inclusion_percent: see above functions

    code returns a dictionary {district geoid: adjacency graph of approximated district}
        the graphs are returned as networkx objects

    '''
    graph_dict = {}
    for d_geoid in membership.keys():
        indices_in_dist = []
        for j, unit in units.iterrows():
            if membership[d_geoid][unit["geoid"]] > inclusion_percent:
                indices_in_dist.append(j)
        unit_indices = [index in indices_in_dist for index in range(len(units))]
        approx_dist_df = units[unit_indices]

        if len(approx_dist_df)>0:
            #build contiguity matrix - uses rook contiguity - queen is available
            contig_matrix = pysal.weights.Rook.from_dataframe(approx_dist_df, idVariable = "geoid")
            graph = networkx_from_matrix_and_list(contig_matrix.full()[0], contig_matrix.full()[1])
            graph_dict.update({d_geoid:graph})
    return graph_dict

def make_assignment_file(districts, units):
    assignment = {}
    perim_assignment = {}
    for i, dist in districts.iterrows():
        assignment[dist] = []
        perim_assignment[dist] = []
        for j, unit in units.iterrows():
            if unit.geometry.intersects(dist.geometry):
                assignment[dist].append(unit["geoid"])
                if unit.geometry.intersects(dist.geometry.boundary):
                    perim_assignment[dist].append(unit["geoid"])
    return (assignment, perim_assignment)
