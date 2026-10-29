from code_archaeologist.analyzer import analyze_repository
from code_archaeologist.explain import explain_locally

def test_imports_definitions_calls(tmp_path):
    (tmp_path / "app.py").write_text("import os\nclass App:\n def run(self):\n  print('hi')\n", encoding="utf-8")
    graph = analyze_repository(tmp_path)
    assert graph.files_scanned == 1
    assert any(e.relation == "imports" for e in graph.edges)
    assert any(n.kind == "class" and n.label == "App" for n in graph.nodes)
    assert any(e.relation == "calls_reference" for e in graph.edges)

def test_explanation_is_candid_about_limits(tmp_path):
    (tmp_path / "main.py").write_text("def main():\n return 1\n", encoding="utf-8")
    result = explain_locally(analyze_repository(tmp_path), "Explain this")
    assert "No repository code was executed." in result.caveats
