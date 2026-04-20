# GSS Archetype Service

An HTTP service that returns `k` "archetypes" summarizing respondents from the
[General Social Survey](https://gss.norc.org/) (GSS). Given a value of `k`, the
service runs k-means clustering over a curated slice of GSS variables and
returns the resulting cluster centroids as interpretable archetype profiles.

By default the service clusters only the two most recent GSS waves (2022 and
2024) so archetypes reflect contemporary American attitudes rather than a
fifty-year average.

## How it works

1. Load the GSS cumulative data file from `data/gss.dta`.
2. Filter to recent waves (default: `year >= 2022`).
3. Select 10 demographic / attitudinal variables; drop rows with any missing.
4. Standard-scale the ordinal variables and one-hot encode the nominal ones.
5. Run k-means with the requested `k` (deterministic; `random_state=0`,
   `n_init=10`).
6. Inverse-transform each centroid back into GSS scales; take the modal
   category for nominals.

## Running the service

### Prerequisites

Download the GSS cumulative data file (Stata format) from
<https://gss.norc.org/us/en/gss/get-the-data/stata.html>, unzip it, and place
it at `data/gss.dta` (or `data/gss.sav` for SPSS).

### Local

```bash
uv sync
uv run uvicorn gss_archetype_service.service:app --reload
```

Service runs on <http://127.0.0.1:8000>. Swagger UI at `/docs`.

### Docker

```bash
docker build -t gss-archetype-service .
docker run -p 127.0.0.1:8000:8000 -v $(pwd)/data:/app/data gss-archetype-service
```

The `-v` mount is required — the image intentionally does not bake in the GSS
data file.

## API

### `GET /archetypes`

Query parameters:

| param      | type | default | description                                       |
|------------|------|---------|---------------------------------------------------|
| `k`        | int  | —       | Number of archetypes to produce. Must be `>= 1`. |
| `min_year` | int  | `2022`  | Earliest GSS wave to include.                    |

Returns a JSON array of `k` archetype objects.

### `GET /health`

Simple status probe; returns `{ "status": "ok", "rows_loaded": <int> }`.

## Interpreting the response

Each archetype object has this shape:

```json
{
  "size": 1418,
  "share": 0.235,
  "age": 30.43,
  "educ": 13.19,
  "polviews": 3.72,
  "partyid": 3.08,
  "attend": 1.30,
  "happy": 2.15,
  "sex": "female",
  "race": "white",
  "marital": "never married",
  "relig": "none"
}
```

### Cluster metadata

| Field   | Meaning                                                                 |
|---------|-------------------------------------------------------------------------|
| `size`  | Number of respondents assigned to this cluster.                         |
| `share` | Fraction of the sample this cluster represents (all shares sum to ~1). |

### Ordinal fields (floats — cluster-mean position on the original scale)

| Field      | Scale | Interpretation                                                                                                                                                     |
|------------|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `age`      | years | Respondent age. Any value is meaningful as-is.                                                                                                                     |
| `educ`     | years | Years of formal education completed. Roughly: 12 = high-school grad, 14 = associate/some college, 16 = bachelor's, 18+ = graduate.                                  |
| `polviews` | 1–7   | Political views. 1 = extremely liberal, 2 = liberal, 3 = slightly liberal, 4 = moderate, 5 = slightly conservative, 6 = conservative, 7 = extremely conservative. |
| `partyid`  | 0–7   | Party identification. 0 = strong Democrat, 1 = not-very-strong Democrat, 2 = independent leans Democrat, 3 = independent, 4 = independent leans Republican, 5 = not-very-strong Republican, 6 = strong Republican, 7 = other party. |
| `attend`   | 0–8   | Frequency of attending religious services. 0 = never, 1 = less than once a year, 2 = once or twice a year, 3 = several times a year, 4 = about once a month, 5 = 2–3 times a month, 6 = nearly every week, 7 = every week, 8 = several times a week. |
| `happy`    | 1–3   | Self-reported happiness. **Lower is happier:** 1 = very happy, 2 = pretty happy, 3 = not too happy.                                                               |

Ordinal values are returned as floats because they are cluster averages. A
`polviews` of `3.72` means the cluster sits just on the liberal side of
moderate.

### Nominal fields (strings — modal category within the cluster)

Each nominal field is the single most common category for respondents in the
cluster. The full distribution is not exposed.

**`sex`** — `male`, `female`.

**`race`** — `white`, `black`, `other`.

**`marital`** — `married`, `widowed`, `divorced`, `separated`, `never married`.

**`relig`** — `protestant`, `catholic`, `jewish`, `none`, `other`, `buddhism`,
`hinduism`, `other eastern religions`, `muslim/islam`, `orthodox-christian`,
`christian`, `native american`, `inter-nondenominational`.

> **Caveat on modal labels:** When a cluster is roughly balanced on a nominal
> variable (e.g., 52% female / 48% male), the modal label wins by a thin
> margin and hides the split. Don't over-index on these when the cluster is
> close to 50/50.

## Project layout

```
gss_archetype_service/
    loader.py       load_gss(), load_value_labels()
    preprocess.py   ColumnTransformer pipeline (scale + one-hot)
    cluster.py      KMeans primitive
    archetypes.py   build_archetypes() — composes load → filter → preprocess → cluster
    interpret.py    centroid → human-readable dict
    service.py      FastAPI app
data/               (gitignored) — place gss.dta here
```

## Customizing the variable set

The clustering variables are defined in `gss_archetype_service/preprocess.py`
as `ORDINAL_COLUMNS` and `NOMINAL_COLUMNS`. Edit those lists to change which
GSS variables shape the archetypes. Make sure any new variables exist in the
GSS cumulative file and have meaningful coverage across `min_year` onward.
