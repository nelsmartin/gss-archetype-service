from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ORDINAL_COLUMNS = ["age", "educ", "polviews", "partyid", "attend", "happy"]
NOMINAL_COLUMNS = ["sex", "race", "marital", "relig"]
FEATURE_COLUMNS = ORDINAL_COLUMNS + NOMINAL_COLUMNS


@dataclass
class PreprocessResult:
    X: np.ndarray
    preprocessor: ColumnTransformer
    feature_names: list[str]
    cleaned: pd.DataFrame


def build_preprocessor(
    ordinal: list[str] = ORDINAL_COLUMNS,
    nominal: list[str] = NOMINAL_COLUMNS,
) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("ordinal", StandardScaler(), ordinal),
            ("nominal", OneHotEncoder(sparse_output=False, handle_unknown="ignore"), nominal),
        ]
    )


def preprocess(
    df: pd.DataFrame,
    ordinal: list[str] = ORDINAL_COLUMNS,
    nominal: list[str] = NOMINAL_COLUMNS,
) -> PreprocessResult:
    cols = ordinal + nominal
    cleaned = df[cols].dropna().reset_index(drop=True)
    preprocessor = build_preprocessor(ordinal, nominal)
    X = preprocessor.fit_transform(cleaned)
    feature_names = preprocessor.get_feature_names_out().tolist()
    return PreprocessResult(X=X, preprocessor=preprocessor, feature_names=feature_names, cleaned=cleaned)
