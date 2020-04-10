#!/usr/bin/env python3
# encoding: UTF-8

"""
Filename: generate_graph_data.py
Author:   David Oniani
E-mail:   oniani.david@mayo.edu

Description:
    Build a graph (CSV file) out of CSV file.
"""

import os
import csv

import pandas as pd

from typing import Dict

DATA_DIR: str = "data"
DATA_FILE: str = "CIDO.csv"


def main() -> None:
    """The main function. Data extraction is done here."""

    # Read the data
    data = pd.read_csv(os.path.join(DATA_DIR, DATA_FILE))
    sources = data["Class ID"]
    parents = data["Parents"]
    preferred_labels = data["Preferred Label"]

    # Build a DIRECTED graph mapping sources to preferred labels
    #
    # NOTE: There are only 611 (out of 2722) nodes that Class IDs (sources) and
    #       Parents (targets) share
    sources_preferred_labels = {
        node: preferred_labels[idx] for idx, node in enumerate(sources)
    }

    # Build an UNDIRECTED graph mapping sources to the dictionary of targets
    # (parents) mapping to the text
    graph: Dict[str, Dict[str, str]] = {}
    for idx, node in enumerate(sources):
        text = preferred_labels[idx]
        parent = parents[idx]

        parent_text = (
            sources_preferred_labels[parent]
            if parent in sources_preferred_labels
            else "NA"
        )

        graph[node] = {"parent": parent, "text": text}
        graph[parent] = {"parent": node, "text": parent_text}

    # Write to a CSV file
    with open(os.path.join(DATA_DIR, "data.csv"), "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["node", "parent", "text"])  # Header
        for node in graph:
            writer.writerow([node, graph[node]["parent"], graph[node]["text"]])


if __name__ == "__main__":
    main()
