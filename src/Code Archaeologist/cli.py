from pathlib import Path
import typer
from code_archaeologist.analyzer import analyze_repository
from code_archaeologist.explain import explain_locally
from code_archaeologist.models import AnalysisGraph

app = typer.Typer(no_args_is_help=True, help="Evidence-grounded codebase exploration.")

@app.command()
def analyze(path: Path = typer.Argument(Path("."), exists=True, file_okay=False),
            out: Path = typer.Option(Path("graph.json"), "--out", "-o")):
    try:
        graph = analyze_repository(path)
    except (OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    out.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(f"Analyzed {graph.files_scanned} files; {len(graph.nodes)} nodes; {len(graph.edges)} edges.")
    typer.echo(f"Graph written to {out}")

@app.command()
def summary(graph_file: Path = typer.Argument(..., exists=True, dir_okay=False)):
    graph = AnalysisGraph.model_validate_json(graph_file.read_text(encoding="utf-8"))
    typer.echo(f"Root: {graph.root}\nFiles scanned: {graph.files_scanned}; skipped: {graph.files_skipped}")
    typer.echo(f"Nodes: {len(graph.nodes)}; edges: {len(graph.edges)}")
    for warning in graph.warnings:
        typer.echo(f"WARNING: {warning}")

@app.command()
def explain(graph_file: Path = typer.Argument(..., exists=True, dir_okay=False),
            question: str = typer.Argument(...)):
    graph = AnalysisGraph.model_validate_json(graph_file.read_text(encoding="utf-8"))
    typer.echo(explain_locally(graph, question).model_dump_json(indent=2))

if __name__ == "__main__":
    app()
