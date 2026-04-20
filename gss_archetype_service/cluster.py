from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans


@dataclass
class ClusterResult:
    centroids: np.ndarray
    labels: np.ndarray
    sizes: np.ndarray
    model: KMeans


def cluster(X: np.ndarray, k: int, random_state: int = 0) -> ClusterResult:
    model = KMeans(n_clusters=k, n_init=10, random_state=random_state)
    labels = model.fit_predict(X)
    sizes = np.bincount(labels, minlength=k)
    return ClusterResult(centroids=model.cluster_centers_, labels=labels, sizes=sizes, model=model)
