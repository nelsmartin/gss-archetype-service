import pytest

from gss_archetype_service.archetypes import build_archetypes
from gss_archetype_service.interpret import interpret


def test_interpret_returns_one_dict_per_cluster(synthetic_gss, fake_value_labels):
    result = build_archetypes(k=3, df=synthetic_gss)
    archetypes = interpret(result, fake_value_labels)
    assert len(archetypes) == 3


def test_interpret_fields_have_correct_types_and_ranges(synthetic_gss, fake_value_labels):
    result = build_archetypes(k=3, df=synthetic_gss)
    archetypes = interpret(result, fake_value_labels)

    for a in archetypes:
        # Metadata
        assert isinstance(a["size"], int)
        assert a["size"] > 0
        assert 0.0 <= a["share"] <= 1.0

        # Ordinals back on original scales
        assert 1.0 <= a["polviews"] <= 7.0
        assert 0.0 <= a["partyid"] <= 7.0
        assert 0.0 <= a["attend"] <= 8.0
        assert 1.0 <= a["happy"] <= 3.0

        # Nominals are human-readable strings from the label map
        assert a["sex"] in {"male", "female"}
        assert a["race"] in {"white", "black", "other"}
        assert a["marital"] in {"married", "widowed", "divorced", "separated", "never married"}
        assert a["relig"] in {"protestant", "catholic", "jewish", "none"}


def test_interpret_shares_sum_to_one(synthetic_gss, fake_value_labels):
    result = build_archetypes(k=4, df=synthetic_gss)
    archetypes = interpret(result, fake_value_labels)
    total_share = sum(a["share"] for a in archetypes)
    assert total_share == pytest.approx(1.0, abs=1e-3)
