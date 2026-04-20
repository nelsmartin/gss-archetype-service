from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer

from gss_archetype_service.cluster import cluster
from gss_archetype_service.loader import load_gss
from gss_archetype_service.preprocess import FEATURE_COLUMNS, preprocess

DEFAULT_MIN_YEAR = 2022


@dataclass
class ArchetypeResult:
    centroids: np.ndarray
    sizes: np.ndarray
    feature_names: list[str]
    preprocessor: ColumnTransformer
    cleaned: pd.DataFrame


def build_archetypes(
    k: int,
    min_year: int = DEFAULT_MIN_YEAR,
    df: pd.DataFrame | None = None,
) -> ArchetypeResult:
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    if df is None:
        df = load_gss(columns=["year"] + FEATURE_COLUMNS)
    recent = df[df["year"] >= min_year]
    pre = preprocess(recent)
    if k > len(pre.cleaned):
        raise ValueError(f"k={k} exceeds available rows ({len(pre.cleaned)}) for min_year={min_year}")
    result = cluster(pre.X, k)
    return ArchetypeResult(
        centroids=result.centroids,
        sizes=result.sizes,
        feature_names=pre.feature_names,
        preprocessor=pre.preprocessor,
        cleaned=pre.cleaned,
    )
