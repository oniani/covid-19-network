#!/usr/bin/env python3
# encoding: UTF-8

"""
Filename: generate_edges_features_data.py
Author:   David Oniani
E-mail:   oniani.david@mayo.edu

Description:
    Build edges and features data files to then create a matrix.
"""

import os
import csv

import pandas as pd

from typing import Dict, List

DATA_DIR: str = "data"
DATA_FILE: str = "data.csv"

EDGES_DATA: str = "edges.csv"
FEATS_DATA: str = "features.csv"


def main() -> None:
    """The main function. Data extraction is done here."""

    # Read the data
    data = pd.read_csv(os.path.join(DATA_DIR, DATA_FILE))
    nodes = data["node_1"]
    parents = data["node_2"]

    # Create node encoding
    temp = list(nodes)
    temp.extend(parents)

    # NOTE: `all_nodes` defines the order in which the features data is built
    all_nodes: List[str] = []
    for item in temp:
        if item not in all_nodes:
            all_nodes.append(item)

    node_encoding: Dict[str, int] = {
        node: idx for idx, node in enumerate(all_nodes)
    }

    # Create edges file
    with open(os.path.join(DATA_DIR, EDGES_DATA), "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        # writer.writerow(["source_idx", "target_idx"])  # Header
        for node, parent in zip(nodes, parents):
            writer.writerow([node_encoding[node], node_encoding[parent]])
            # NOTE: Uncomment the line below to generate duplicate edges
            # writer.writerow([node_encoding[parent], node_encoding[node]])

    # Creates features file
    with open(os.path.join(DATA_DIR, FEATS_DATA), "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["idx", "source_idx", "feature"])  # Header
        for idx, node in enumerate(all_nodes):
            writer.writerow([idx, node_encoding[node], 0])


if __name__ == "__main__":
    main()
