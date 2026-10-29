from code_archaeologist.models import AnalysisGraph, Explanation

def explain_locally(graph: AnalysisGraph, question: str) -> Explanation:
    q = question.strip()
    if not q:
        raise ValueError("Question must not be empty.")
    imports = sum(e.relation in {"imports", "imports_from"} for e in graph.edges)
    calls = sum(e.relation == "calls_reference" for e in graph.edges)
    definitions = [n for n in graph.nodes if n.kind in {"function", "class"}]
    answer = (f"Analyzed {graph.files_scanned} supported file(s): {len(graph.nodes)} nodes, "
              f"{len(graph.edges)} evidence edges, {imports} import edges, {calls} unresolved "
              f"call references and {len(definitions)} function/class definitions. "
              "This offline response summarizes recorded syntax; it does not infer runtime behavior.")
    return Explanation(question=q, answer=answer, evidence_node_ids=[n.id for n in definitions[:20]],
                       caveats=["Only Python AST analysis is implemented in M1.",
                                "Call references are syntactic and may not resolve at runtime.",
                                "No repository code was executed.",
                                "This is a deterministic local summary, not an AI-generated explanation."])
