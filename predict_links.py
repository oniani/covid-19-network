#!/usr/bin/env python3
# encoding: UTF-8

"""
Filename: predict_links.py
Author:   David Oniani
E-mail:   oniani.david@mayo.edu

Description:
    Use node2vec for link prediction.
"""

import os
import pickle

import node2vec

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import scipy.sparse as sp

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score

from src.preprocessing import mask_test_edges
from src import node2vec

from gensim.models import Word2Vec


NETWORK_DIR = "pickle"
PICKLE_FILE = "adj_feat.pkl"


def main() -> None:
    """The main function. Link prediction is done here."""

    # Load pickled (adj, feat) tuple
    with open(os.path.join(NETWORK_DIR, PICKLE_FILE), "rb") as file:
        adj, features = pickle.load(file)

    g = nx.Graph(adj)  # Recreate graph using node indices (0 to num_nodes-1)

    # Draw the network
    # nx.draw_networkx(g, with_labels=False, node_size=50, node_color="r")
    # plt.show()

    # Preprocessing (train/test split)
    np.random.seed(0)  # make sure train-test split is consistent
    adj_sparse = nx.to_scipy_sparse_matrix(g)

    # Perform train-test split
    (
        adj_train,
        train_edges,
        train_edges_false,
        val_edges,
        val_edges_false,
        test_edges,
        test_edges_false,
    ) = mask_test_edges(adj_sparse, test_frac=0.3, val_frac=0.1)

    # new graph object with only non-hidden edges
    g_train = nx.from_scipy_sparse_matrix(adj_train)

    # Inspect train/test split
    print("Total nodes:", adj_sparse.shape[0])

    # adj is symmetric, so nnz (num non-zero) = 2 * num_edges
    print("Total edges:", int(adj_sparse.nnz / 2))
    print("Training edges (positive):", len(train_edges))
    print("Training edges (negative):", len(train_edges_false))
    print("Validation edges (positive):", len(val_edges))
    print("Validation edges (negative):", len(val_edges_false))
    print("Test edges (positive):", len(test_edges))
    print("Test edges (negative):", len(test_edges_false))

    # Train node2vec (Learn Node Embeddings)

    # node2vec settings
    # NOTE: When p = q = 1, this is equivalent to DeepWalk

    P = 1  # Return hyperparameter
    Q = 1  # In-out hyperparameter
    WINDOW_SIZE = 10  # Context size for optimization
    NUM_WALKS = 10  # Number of walks per source
    WALK_LENGTH = 80  # Length of walk per source
    DIMENSIONS = 128  # Embedding dimension
    DIRECTED = False  # Graph directed/undirected
    WORKERS = 8  # Num. parallel workers
    ITER = 1  # SGD epochs

    # Preprocessing, generate walks

    # create node2vec graph instance
    g_n2v = node2vec.Graph(g_train, DIRECTED, P, Q)
    g_n2v.preprocess_transition_probs()
    walks = g_n2v.simulate_walks(NUM_WALKS, WALK_LENGTH)
    walks = [list(map(str, walk)) for walk in walks]

    # Train skip-gram model
    model = Word2Vec(
        walks,
        size=DIMENSIONS,
        window=WINDOW_SIZE,
        min_count=0,
        sg=1,
        workers=WORKERS,
        iter=ITER,
    )

    # Store embeddings mapping
    emb_mappings = model.wv

    print(emb_mappings)

    # Create node embeddings matrix (rows = nodes, columns = embedding features)
    emb_list = []
    for node_index in range(0, adj_sparse.shape[0]):
        node_str = str(node_index)
        node_emb = emb_mappings[node_str]
        emb_list.append(node_emb)
    emb_matrix = np.vstack(emb_list)

    def get_edge_embeddings(edge_list):
        """
        Generate bootstrapped edge embeddings (as is done in node2vec paper)
        Edge embedding for (v1, v2) = hadamard product of node embeddings for
        v1, v2.
        """
        embs = []
        for edge in edge_list:
            node1 = edge[0]
            node2 = edge[1]
            emb1 = emb_matrix[node1]
            emb2 = emb_matrix[node2]
            edge_emb = np.multiply(emb1, emb2)
            embs.append(edge_emb)
        embs = np.array(embs)
        return embs

    # Train-set edge embeddings
    pos_train_edge_embs = get_edge_embeddings(train_edges)
    neg_train_edge_embs = get_edge_embeddings(train_edges_false)
    train_edge_embs = np.concatenate(
        [pos_train_edge_embs, neg_train_edge_embs]
    )

    # Create train-set edge labels: 1 = real edge, 0 = false edge
    train_edge_labels = np.concatenate(
        [np.ones(len(train_edges)), np.zeros(len(train_edges_false))]
    )

    # Val-set edge embeddings, labels
    pos_val_edge_embs = get_edge_embeddings(val_edges)
    neg_val_edge_embs = get_edge_embeddings(val_edges_false)
    val_edge_embs = np.concatenate([pos_val_edge_embs, neg_val_edge_embs])
    val_edge_labels = np.concatenate(
        [np.ones(len(val_edges)), np.zeros(len(val_edges_false))]
    )

    # Test-set edge embeddings, labels
    pos_test_edge_embs = get_edge_embeddings(test_edges)
    neg_test_edge_embs = get_edge_embeddings(test_edges_false)
    test_edge_embs = np.concatenate([pos_test_edge_embs, neg_test_edge_embs])

    # Create val-set edge labels: 1 = real edge, 0 = false edge
    test_edge_labels = np.concatenate(
        [np.ones(len(test_edges)), np.zeros(len(test_edges_false))]
    )

    # Train logistic regression classifier on train-set edge embeddings
    edge_classifier = LogisticRegression(random_state=0)
    edge_classifier.fit(train_edge_embs, train_edge_labels)

    # Predicted edge scores: probability of being of class "1" (real edge)
    val_preds = edge_classifier.predict_proba(val_edge_embs)[:, 1]
    val_roc = roc_auc_score(val_edge_labels, val_preds)
    val_ap = average_precision_score(val_edge_labels, val_preds)

    # Predicted edge scores: probability of being of class "1" (real edge)
    test_preds = edge_classifier.predict_proba(test_edge_embs)[:, 1]
    test_roc = roc_auc_score(test_edge_labels, test_preds)
    test_ap = average_precision_score(test_edge_labels, test_preds)

    print("node2vec Validation ROC score: ", str(val_roc))
    print("node2vec Validation AP score: ", str(val_ap))
    print("node2vec Test ROC score: ", str(test_roc))
    print("node2vec Test AP score: ", str(test_ap))


if __name__ == "__main__":
    main()
