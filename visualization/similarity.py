import csv

from typing import Any, List, Tuple

from gensim.models import KeyedVectors


def top_10_data() -> Tuple[Any, Any, Any]:
    """Read the data for Top 10."""

    node_dict = {}
    node_reverse_dict = {}
    reader = csv.reader(
        open("../combined_graph/Combined_Dict.txt"), delimiter=";"
    )
    for row in reader:
        node_dict[row[0]] = row[1]
        node_reverse_dict[row[1]] = row[0]

    emb_mappings = KeyedVectors.load_word2vec_format(
        "../combined_graph/CombineGraph-nonDupe.emd", binary=False
    )

    return emb_mappings, node_dict, node_reverse_dict


def top_10(node: str, node_data: Tuple[Any, Any, Any]) -> List:
    """Give top 10 most similar nodes for the given node."""

    emb_mappings, node_dict, node_reverse_dict = node_data

    try:
        index = node_dict[node]
    except KeyError:
        return []

    s2 = emb_mappings.most_similar(index)
    top_10: List[str] = []
    similarities: List[float] = []
    for tup in s2:
        try:
            name = node_reverse_dict[tup[0]]
        except KeyError:
            name = "NA"

        similarity: float = tup[1]
        similarities.append(similarity)

        if "@" in name:
            top_10.append(name.split("@")[0])
        else:
            top_10.append(name)

    return [top_10, similarities]
