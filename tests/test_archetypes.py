import pytest

from gss_archetype_service.archetypes import build_archetypes


def test_build_archetypes_composes_pipeline(synthetic_gss):
    result = build_archetypes(k=4, min_year=2022, df=synthetic_gss)
    assert result.centroids.shape[0] == 4
    assert result.sizes.sum() == len(result.cleaned)
    assert len(result.sizes) == 4


def test_build_archetypes_rejects_invalid_k(synthetic_gss):
    with pytest.raises(ValueError):
        build_archetypes(k=0, df=synthetic_gss)


def test_build_archetypes_rejects_k_exceeding_rows(synthetic_gss):
    with pytest.raises(ValueError):
        build_archetypes(k=10_000, df=synthetic_gss)


def test_build_archetypes_respects_min_year(synthetic_gss):
    # min_year=2099 means no rows survive the filter, so preprocess yields empty,
    # and any k >= 1 must fail the k-vs-rows guardrail.
    with pytest.raises(ValueError):
        build_archetypes(k=1, min_year=2099, df=synthetic_gss)
