import numpy as np

from gss_archetype_service.preprocess import ORDINAL_COLUMNS, preprocess


def test_preprocess_returns_scaled_matrix(synthetic_gss):
    result = preprocess(synthetic_gss)
    assert result.X.shape[0] == len(synthetic_gss)
    assert result.X.shape[1] > len(ORDINAL_COLUMNS)  # one-hot widens beyond ordinal count

    n_ordinal = len(ORDINAL_COLUMNS)
    np.testing.assert_allclose(result.X[:, :n_ordinal].mean(axis=0), 0, atol=1e-10)
    np.testing.assert_allclose(result.X[:, :n_ordinal].std(axis=0), 1, atol=1e-10)


def test_preprocess_drops_rows_with_missing(synthetic_gss):
    synthetic_gss.loc[0, "polviews"] = np.nan
    synthetic_gss.loc[5, "sex"] = np.nan
    result = preprocess(synthetic_gss)
    assert len(result.cleaned) == len(synthetic_gss) - 2


def test_preprocess_feature_names_include_ordinals_and_nominals(synthetic_gss):
    result = preprocess(synthetic_gss)
    names = result.feature_names
    assert any(n.startswith("ordinal__age") for n in names)
    assert any(n.startswith("nominal__sex_") for n in names)
