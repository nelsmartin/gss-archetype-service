import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from gss_archetype_service import service
from gss_archetype_service.service import app


@pytest.fixture
def synthetic_gss() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 200
    return pd.DataFrame({
        "year":     rng.choice([2022, 2024], n),
        "age":      rng.integers(18, 90, n).astype(float),
        "educ":     rng.integers(8, 20, n).astype(float),
        "polviews": rng.integers(1, 8, n).astype(float),
        "partyid":  rng.integers(0, 8, n).astype(float),
        "attend":   rng.integers(0, 9, n).astype(float),
        "happy":    rng.integers(1, 4, n).astype(float),
        "sex":      rng.choice([1.0, 2.0], n),
        "race":     rng.choice([1.0, 2.0, 3.0], n),
        "marital":  rng.choice([1.0, 2.0, 3.0, 4.0, 5.0], n),
        "relig":    rng.choice([1.0, 2.0, 3.0, 4.0], n),
    })


@pytest.fixture
def fake_value_labels() -> dict[str, dict[int, str]]:
    return {
        "sex":      {1: "male", 2: "female"},
        "race":     {1: "white", 2: "black", 3: "other"},
        "marital":  {1: "married", 2: "widowed", 3: "divorced", 4: "separated", 5: "never married"},
        "relig":    {1: "protestant", 2: "catholic", 3: "jewish", 4: "none"},
        "polviews": {1: "extremely liberal", 7: "extremely conservative"},
        "partyid":  {0: "strong democrat", 6: "strong republican"},
        "attend":   {0: "never", 8: "several times a week"},
        "happy":    {1: "very happy", 3: "not too happy"},
    }


@pytest.fixture
def client(synthetic_gss, fake_value_labels):
    # Bypass lifespan by instantiating TestClient without the `with` context;
    # pre-populate state directly so the handlers have what they need.
    service.state["df"] = synthetic_gss
    service.state["value_labels"] = fake_value_labels
    yield TestClient(app)
    service.state.clear()


@pytest.fixture
def auth_headers():
    from gss_archetype_service.auth import issue_token
    return {"Authorization": f"Bearer {issue_token('test-user')}"}
