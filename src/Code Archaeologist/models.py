from pydantic import BaseModel, Field

class SourceLocation(BaseModel):
    path: str
    line: int = Field(ge=1)
    column: int = Field(default=1, ge=1)

class Node(BaseModel):
    id: str
    kind: str
    label: str
    language: str
    location: SourceLocation | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

class Edge(BaseModel):
    source: str
    target: str
    relation: str
    evidence_kind: str
    confidence: float = Field(ge=0.0, le=1.0)
    location: SourceLocation | None = None
    note: str | None = None

class AnalysisGraph(BaseModel):
    schema_version: str = "1.0"
    root: str
    nodes: list[Node]
    edges: list[Edge]
    warnings: list[str] = Field(default_factory=list)
    files_scanned: int = 0
    files_skipped: int = 0

class Explanation(BaseModel):
    question: str
    answer: str
    evidence_node_ids: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    provider: str = "local-deterministic"
