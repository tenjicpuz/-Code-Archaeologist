import os
from pathlib import Path
from code_archaeologist.adapters.python_ast import PythonAstAdapter
from code_archaeologist.models import AnalysisGraph

IGNORES = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", "target", ".next", ".tox"}
MAX_FILE_BYTES, MAX_FILES = 1_000_000, 20_000

def analyze_repository(root: str | Path) -> AnalysisGraph:
    base = Path(root).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError("Repository path must be a directory.")
    adapter = PythonAstAdapter()
    nodes, edges, warnings = [], [], []
    scanned = skipped = 0
    for current, dirs, filenames in os.walk(base, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORES and not (Path(current) / d).is_symlink())
        for name in sorted(filenames):
            path = Path(current) / name
            if path.suffix.lower() not in adapter.extensions:
                continue
            if path.is_symlink():
                skipped += 1
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    skipped += 1
                    warnings.append(f"{path.relative_to(base)}: skipped (>1 MB).")
                    continue
            except OSError:
                skipped += 1
                continue
            scanned += 1
            if scanned > MAX_FILES:
                warnings.append(f"Stopped at safety limit of {MAX_FILES} files.")
                break
            rel = path.relative_to(base).as_posix()
            new_nodes, new_edges, new_warnings = adapter.analyze_file(path, rel)
            nodes.extend(new_nodes); edges.extend(new_edges); warnings.extend(new_warnings)
    if scanned == 0:
        warnings.append("No supported Python files found; more language adapters are planned.")
    return AnalysisGraph(root=str(base), nodes=nodes, edges=edges, warnings=warnings,
                         files_scanned=min(scanned, MAX_FILES), files_skipped=skipped)
