#!/usr/bin/env python3
# encoding: UTF-8

"""
Filename: generate_graph.py
Author:   David Oniani
E-mail:   oniani.david@mayo.edu

Description:
    Create a pickle file for use in node2vec.
"""

import os
import pickle

import networkx as nx
import numpy as np
import pandas as pd


EDGES_FILE: str = "data/edges.csv"
FEATS_FILE: str = "data/features.csv"

PICKLE_DIR: str = "pickle"
PICKLE_FILE: str = "adj_feat.pkl"


def main() -> None:
    """The main function."""

    # Read edge list
    g = nx.read_edgelist(EDGES_FILE, delimiter=",", nodetype=int)

    # Add root
    # NOTE: The root is directly connected to all other nodes
    g.add_node(int(0))

    for node in g.nodes():
        if node != int(0):
            g.add_edge(int(0), node)

    # Read feature list
    df = pd.read_csv(FEATS_FILE, index_col=0)

    # Add features from dataframe to networkx nodes
    for node_idx, features_series in df.iterrows():
        if not g.has_node(node_idx):
            g.add_node(node_idx)
            g.add_edge(node_idx, int(0))

        g.nodes[node_idx]["features"] = features_series.values

    # Make sure the graph is connected
    assert nx.is_connected(g) is True

    # Get adjacency matrix in sparse format (sorted by g.nodes())
    adj = nx.adjacency_matrix(g)

    # Get features matrix (also sorted by g.nodes())
    features = np.zeros((df.shape[0], df.shape[1]))  # num nodes, num features

    for idx, node in enumerate(g.nodes()):
        features[idx, :] = g.nodes[node]["features"]

    # Save adj, features in pickle file
    network_tuple = (adj, features)

    with open(os.path.join(PICKLE_DIR, PICKLE_FILE), "wb") as f:
        pickle.dump(network_tuple, f)


if __name__ == "__main__":
    main()
