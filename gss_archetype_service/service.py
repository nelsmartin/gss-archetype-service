from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query

from gss_archetype_service.archetypes import DEFAULT_MIN_YEAR, build_archetypes
from gss_archetype_service.auth import TokenRequest, TokenResponse, issue_token, require_auth
from gss_archetype_service.interpret import interpret
from gss_archetype_service.loader import load_gss, load_value_labels
from gss_archetype_service.preprocess import FEATURE_COLUMNS
from gss_archetype_service.schemas import Archetype, HealthResponse

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["df"] = load_gss(columns=["year"] + FEATURE_COLUMNS)
    state["value_labels"] = load_value_labels()
    yield
    state.clear()


app = FastAPI(lifespan=lifespan, title="GSS Archetype Service")


@app.post("/auth/token", response_model=TokenResponse)
def auth_token(req: TokenRequest):
    # Toy issuer: accepts any username. A real system would verify credentials
    # or broker an OAuth flow with an external identity provider.
    return TokenResponse(access_token=issue_token(subject=req.username))


@app.get("/archetypes", response_model=list[Archetype])
def get_archetypes(
    k: int = Query(..., ge=1, description="Number of archetypes to produce"),
    min_year: int = Query(DEFAULT_MIN_YEAR, ge=1972, description="Earliest GSS wave to include"),
    _: dict = Depends(require_auth),
):
    try:
        result = build_archetypes(k=k, min_year=min_year, df=state["df"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return interpret(result, state["value_labels"])


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "rows_loaded": len(state.get("df", []))}
