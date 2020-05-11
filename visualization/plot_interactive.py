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
    similarities: List[List[float]] = []

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
        top = top_10(row_cors[0], node_data)

        if len(top) == 2:
            top_10s.append(", ".join(top[0]))
            similarities.append(top[1])

        elif len(top) == 1:
            if top[0]:
                top_10s.append(", ".join(top[0]))
            elif top[1]:
                similarities.append(top[1])

        elif len(top) == 0:
            top_10s.append("")
            similarities.append([])

    # Cleanup
    names = [name.replace("  ", " ").replace("\t", " ") for name in names]

    # Create a dataframe
    df = pd.DataFrame(
        {
            "name": names,
            "cluster": clusters,
            "category": categories,
            "x": x_cors,
            "y": y_cors,
            "top10": top_10s,
            "similarity": similarities,
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

    # output_file(
    #     "graph.html",
    #     title="COVID-19 Co-occurence Network Embeddings Visualization",
    # )
    # show(plot)

    # CODE GENERATION -- MIGHT LOOK UGLY
    with open("search.html", "w") as file:

        file.write("<!DOCTYPE html>\n")
        file.write('<html lang="en">\n')
        file.write("  <head>\n")
        file.write('    <meta charset="utf-8">\n')

        file.write(
            '    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>\n'
        )
        file.write(
            '    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">\n'
        )

        file.write(
            '    <script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/js/select2.min.js"></script>\n'
        )

        file.write(
            '    <link href="https://cdn.jsdelivr.net/npm/select2@4.0.13/dist/css/select2.min.css" rel="stylesheet" />\n'
        )

        file.write("  <head>\n")
        file.write("  <body>\n")

        file.write('    <div class="container">\n')
        file.write('      <div class="row mt-2 mx-auto">\n')
        file.write('        <div class="col">\n')

        # Selection
        file.write('          <select id="search" class="btn form-control">\n')

        names_cats = dict(zip(names, categories))
        for name, category, top, similarity in zip(
            df["name"], df["category"], df["top10"], df["similarity"]
        ):
            similarity = ", ".join([str(i) for i in similarity])

            try:
                types = ", ".join([names_cats[name] for name in top])
            except KeyError:
                types = ", ".join(["NA"] * 10)

            file.write(
                f'            <option value="{name} ({category})" name="{name}" types="{types}" top="{top}" similarity="{similarity}">{name} ({category})</option>\n'
            )

        file.write("          </select>\n")

        # Table
        file.write("        </div>\n")
        file.write("      </div>\n")
        file.write('      <div class="row mt-2 mx-auto">\n')
        file.write('        <div class="col">\n')
        file.write(
            '          <table id="similarityTable" class="table table-striped">\n'
        )
        file.write('            <thead class="thead-light">\n')
        file.write("              <tr>\n")
        file.write('                <th scope="col">Name</th>\n')
        file.write('                <th scope="col">Type</th>\n')
        file.write('                <th scope="col">Association</th>\n')
        file.write('                <th scope="col">Cosine Similarity</th>\n')
        file.write("              <tr>\n")
        file.write("            <thead>\n")
        file.write("            <tbody></tbody>\n")
        file.write("          <table>\n")
        file.write("        </div>\n")
        file.write("      </div>\n")
        file.write("    <div>\n")

        # Scripts
        file.write(
            '  <script>$("#search").select2({ placeholder: "Select an entity" });</script>\n'
        )

        file.write(
            '  <script>$("#search").on("select2:select", function(e) { '
            "let attrs = e.params.data.element.attributes; "
            "let name = attrs.name.nodeValue; "
            'let tops = attrs.top.nodeValue.split(","); '
            'let types = attrs.types.nodeValue.split(","); '
            'let sims = attrs.similarity.nodeValue.split(","); '
            "console.log(attrs); "
            '$("#similarityTable tbody").empty(); '
            "tops.forEach((top, idx) => { "
            "let sim = sims[idx]; "
            "let type = types[idx]; "
            '$("#similarityTable").append(`<tr><td>${top.trim()}</td><td>${type.trim()}</td><td>${name}</td><td>${sim.trim()}</td></tr>`);}) '
            "})"
            "</script>\n",
        )

        file.write("  <body>\n")
        file.write("</html>\n")


if __name__ == "__main__":
    main()
