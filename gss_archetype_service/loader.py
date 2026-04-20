from pathlib import Path

import pandas as pd
import pyreadstat

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_gss(path: Path | None = None, columns: list[str] | None = None) -> pd.DataFrame:
    path = Path(path) if path else _default_path()
    if path.suffix == ".dta":
        return pd.read_stata(path, columns=columns, convert_categoricals=False)
    if path.suffix == ".sav":
        return pd.read_spss(path, usecols=columns, convert_categoricals=False)
    raise ValueError(f"Unsupported GSS file format: {path.suffix}")


def load_value_labels(path: Path | None = None) -> dict[str, dict[int, str]]:
    path = Path(path) if path else _default_path()
    if path.suffix == ".dta":
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True, encoding="LATIN1")
    elif path.suffix == ".sav":
        _, meta = pyreadstat.read_sav(str(path), metadataonly=True, encoding="LATIN1")
    else:
        raise ValueError(f"Unsupported GSS file format: {path.suffix}")
    out: dict[str, dict[int, str]] = {}
    for var, labelset in meta.variable_to_label.items():
        labels = meta.value_labels.get(labelset, {})
        out[var] = {int(k): v for k, v in labels.items() if isinstance(k, (int, float))}
    return out


def _default_path() -> Path:
    for name in ("gss.dta", "gss.sav"):
        candidate = DATA_DIR / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No GSS file found in {DATA_DIR}. Download the cumulative data file "
        "from https://gss.norc.org/us/en/gss/get-the-data/stata.html and save "
        "it as data/gss.dta"
    )
