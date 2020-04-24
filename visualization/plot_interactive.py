#!/usr/bin/env python3
# encoding: UTF-8

"""
Filename: plot_interactive.py
Author:   David Oniani
E-mail:   oniani.david@mayo.edu

Description:
    Co-occurence graph visualization using Bokeh.
"""

import csv

import pandas as pd

from typing import List

from bokeh.io import output_file, show
from bokeh.models import (
    BoxZoomTool,
    ColumnDataSource,
    HoverTool,
    PanTool,
    ResetTool,
    SaveTool,
    WheelZoomTool,
)
from bokeh.palettes import magma
from bokeh.plotting import figure

from similarity import top_10, top_10_data


def main() -> None:
    """The main function."""

    # Get the data
    reader_cors = csv.reader(
        open("../combined_graph/clusters/node_coordination.txt"), delimiter=";"
    )

    reader_clusters = csv.reader(
        open("../combined_graph/clusters/node_clusters.txt"), delimiter=";"
    )

    node_data = top_10_data()

    # Process the data
    names: List[str] = []
    clusters: List[float] = []
    categories: List[str] = []

    x_cors: List[float] = []
    y_cors: List[float] = []

    top_10s: List[str] = []

    for row_cors, row_clusters in zip(reader_cors, reader_clusters):
        if "@" in row_cors[0]:
            items = row_cors[0].split("@")
            names.append(items[0])
            categories.append(items[1])
        else:
            names.append(row_cors[0])
            categories.append("NA")
        clusters.append(int(row_clusters[1]))
        x_cors.append(float(row_cors[1]))
        y_cors.append(float(row_cors[2]))
        top_10s.append(", ".join(top_10(row_cors[0], node_data)))

    # Create a dataframe
    df = pd.DataFrame(
        {
            "name": names,
            "cluster": clusters,
            "category": categories,
            "x": x_cors,
            "y": y_cors,
            "top10": top_10s,
        }
    )

    # Selecting the colors for each unique category in album_name
    unique_clusters = df["cluster"].unique()
    palette = magma(len(unique_clusters) + 1)

    # Mapping each category with a color of Set2
    colormap = dict(zip(unique_clusters, palette))

    # Making a color column based on album_name
    df["color"] = df["cluster"].map(colormap)

    # Interactive elements
    interactive_tools = [
        HoverTool(
            tooltips=[
                ("name", "@name"),
                ("type", "@category"),
                ("top10", "@top10"),
            ]
        ),
        WheelZoomTool(),
        PanTool(),
        BoxZoomTool(),
        ResetTool(),
        SaveTool(),
    ]

    # Define the plot and add the attributes
    plot = figure(
        tools=interactive_tools,
        title="COVID-19 Co-occurence Network Embeddings Visualization "
        "(by David Oniani and Dr. Feichen Shen)",
        background_fill_color="#fafafa",
        plot_height=300,
        sizing_mode="scale_width",
    )

    plot.toolbar.active_scroll = plot.select_one(WheelZoomTool)

    # Remove redundant elements
    plot.axis.visible = False
    plot.title.align = "center"
    plot.title.text_font_size = "16pt"
    plot.title.text_font_style = "italic"

    # Show (and save) the plot
    plot.circle(
        x="x",
        y="y",
        source=ColumnDataSource(df),
        color="color",
        alpha=0.8,
        size=4.5,
    )

    output_file(
        "graph.html",
        title="COVID-19 Co-occurence Network Embeddings Visualization",
    )
    show(plot)


if __name__ == "__main__":
    main()
