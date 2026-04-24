import numpy as np

from gss_archetype_service.cluster import cluster


def test_cluster_output_shapes():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((100, 8))
    result = cluster(X, k=4)
    assert result.centroids.shape == (4, 8)
    assert result.labels.shape == (100,)
    assert len(result.sizes) == 4
    assert result.sizes.sum() == 100


def test_cluster_is_deterministic():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((100, 8))
    a = cluster(X, k=3)
    b = cluster(X, k=3)
    np.testing.assert_array_equal(a.labels, b.labels)
    np.testing.assert_allclose(a.centroids, b.centroids)
