from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from gss_archetype_service.archetypes import DEFAULT_MIN_YEAR, build_archetypes
from gss_archetype_service.interpret import interpret
from gss_archetype_service.loader import load_gss, load_value_labels
from gss_archetype_service.preprocess import FEATURE_COLUMNS

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["df"] = load_gss(columns=["year"] + FEATURE_COLUMNS)
    state["value_labels"] = load_value_labels()
    yield
    state.clear()


app = FastAPI(lifespan=lifespan, title="GSS Archetype Service")


@app.get("/archetypes")
def get_archetypes(
    k: int = Query(..., ge=1, description="Number of archetypes to produce"),
    min_year: int = Query(DEFAULT_MIN_YEAR, ge=1972, description="Earliest GSS wave to include"),
) -> list[dict]:
    try:
        result = build_archetypes(k=k, min_year=min_year, df=state["df"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return interpret(result, state["value_labels"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "rows_loaded": len(state.get("df", []))}
