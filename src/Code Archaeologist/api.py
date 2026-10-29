from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from code_archaeologist.analyzer import analyze_repository
from code_archaeologist.explain import explain_locally
from code_archaeologist.models import AnalysisGraph, Explanation

app = FastAPI(title="Code Archaeologist API", version="0.1.0",
              description="Local development API; harden before public deployment.")

class AnalyzeRequest(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
class ExplainRequest(BaseModel):
    graph: AnalysisGraph
    question: str = Field(min_length=1, max_length=2000)

@app.get("/health")
def health():
    return {"status": "ok", "analysis": "python-ast-m1", "ai": "not-configured"}

@app.post("/api/analyze", response_model=AnalysisGraph)
def analyze(request: AnalyzeRequest):
    try:
        return analyze_repository(Path(request.path))
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/explain", response_model=Explanation)
def explain(request: ExplainRequest):
    try:
        return explain_locally(request.graph, request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
