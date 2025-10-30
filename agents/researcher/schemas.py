from pydantic import BaseModel, Field


class Summary(BaseModel):
    headline: str
    facts: list[str] = Field(default_factory=list)
    context: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    implications: list[str] = Field(default_factory=list)


class Source(BaseModel):
    title: str
    url: str
    resolved_url: str
    domain: str
    reliability_score: float


class SearchResponse(BaseModel):
    query: str = Field(description="Consulta formateada del usuario")
    date: str = Field(description="fecha de la consulta en formato: aaaa-mm-dd")
    status: str = Field(description="fiabilidad de la investigacion")
    summary: Summary
    sources: list[Source] = Field(default_factory=list)
