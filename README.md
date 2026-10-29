# Code Archaeologist

Evidence-grounded codebase exploration for developers. The CLI and API analyze source as data; they do not execute repository code.

## M1
- Python AST analysis for imports, definitions and syntactic call references
- Shared graph model with source locations, evidence type and confidence
- CLI to export a JSON graph
- FastAPI endpoints and a React + TypeScript dashboard starter
- Offline explanation baseline; no external AI provider is configured yet

## Run
Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
code-archaeologist analyze . --out graph.json
uvicorn code_archaeologist.api:app --reload
```

Frontend: `cd web && npm install && npm run dev`.

## Security
The analyzer does not import or execute project code. It skips common dependency/build directories, symlinks and files larger than 1 MB. The API accepts local filesystem paths and is intended for localhost development only; do not expose it publicly without authentication, sandboxing and request limits. Static analysis cannot prove code is safe.

## Roadmap
M1 Python AST; M2 Tree-sitter and JS/TS; M3 cross-file symbol resolution and impact analysis; M4 opt-in AI explanations with evidence citations; M5 Git history.
