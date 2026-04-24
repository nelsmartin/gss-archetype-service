from pydantic import BaseModel, Field


class Archetype(BaseModel):
    size: int = Field(description="Number of respondents in this cluster")
    share: float = Field(ge=0, le=1, description="Fraction of the sample this cluster represents")

    age: float = Field(description="Mean age in years")
    educ: float = Field(description="Mean years of formal education")
    polviews: float = Field(ge=1, le=7, description="1 = extremely liberal, 7 = extremely conservative")
    partyid: float = Field(ge=0, le=7, description="0 = strong Democrat, 6 = strong Republican, 7 = other")
    attend: float = Field(ge=0, le=8, description="Religious attendance frequency, 0 = never to 8 = several times a week")
    happy: float = Field(ge=1, le=3, description="Self-reported happiness, 1 = very happy to 3 = not too happy")

    sex: str = Field(description="Modal sex in the cluster")
    race: str = Field(description="Modal race in the cluster")
    marital: str = Field(description="Modal marital status in the cluster")
    relig: str = Field(description="Modal religion in the cluster")


class HealthResponse(BaseModel):
    status: str
    rows_loaded: int
