# covid-19-network

## Table of Contents

- [Quickstart](#quickstart)
- [Visualization](#visualization)
- [Developers](#developers)

## Quickstart

```sh
# Install dependencies
python3 -m pip install -r requirements.txt

# Generate data
python3 generate_graph_data.py
python3 generate_edges_features_data.py

# Generate graph
python3 generate_graph.py

# Link prediction
python3 predict_links.py
```

## Visualization

The network is visualized using [Bokeh](https://bokeh.org/) and is available
[here: https://www.davidoniani.com/covid-19-network/](https://www.davidoniani.com/covid-19-network).

## Developers

Developed by David Oniani and Dr. Feichen Shen.
