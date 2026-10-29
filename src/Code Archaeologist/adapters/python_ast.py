import ast
from pathlib import Path
from code_archaeologist.models import Edge, Node, SourceLocation

class PythonAstAdapter:
    name = "python"
    extensions = (".py",)

    def analyze_file(self, path: Path, relative_path: str):
        nodes = [Node(id=f"file:{relative_path}", kind="file", label=relative_path,
                      language="python", location=SourceLocation(path=relative_path, line=1))]
        edges, warnings = [], []
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative_path)
        except (UnicodeDecodeError, SyntaxError, OSError) as exc:
            return nodes, edges, [f"{relative_path}: parse failed ({type(exc).__name__})."]

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                self.add_definition(node, "function")
                self.generic_visit(node)
            def visit_AsyncFunctionDef(self, node):
                self.add_definition(node, "function")
                self.generic_visit(node)
            def visit_ClassDef(self, node):
                self.add_definition(node, "class")
                self.generic_visit(node)
            def add_definition(self, node, kind):
                line, col = node.lineno, node.col_offset + 1
                ident = f"{kind}:{relative_path}:{line}:{node.name}"
                nodes.append(Node(id=ident, kind=kind, label=node.name, language="python",
                                  location=SourceLocation(path=relative_path, line=line, column=col)))
                edges.append(Edge(source=f"file:{relative_path}", target=ident, relation="defines",
                                  evidence_kind="python_ast_definition", confidence=1.0,
                                  location=SourceLocation(path=relative_path, line=line, column=col)))
            def visit_Import(self, node):
                for alias in node.names:
                    target = f"module:{alias.name}"
                    if not any(n.id == target for n in nodes):
                        nodes.append(Node(id=target, kind="module", label=alias.name, language="python"))
                    edges.append(Edge(source=f"file:{relative_path}", target=target, relation="imports",
                                      evidence_kind="python_ast_import", confidence=1.0,
                                      location=SourceLocation(path=relative_path, line=node.lineno, column=node.col_offset + 1),
                                      note="Syntactic import; runtime import success is not verified."))
            def visit_ImportFrom(self, node):
                module = "." * node.level + (node.module or "")
                target = f"module:{module or '<relative-import>'}"
                if not any(n.id == target for n in nodes):
                    nodes.append(Node(id=target, kind="module", label=module or "<relative-import>", language="python"))
                edges.append(Edge(source=f"file:{relative_path}", target=target, relation="imports_from",
                                  evidence_kind="python_ast_import", confidence=1.0,
                                  location=SourceLocation(path=relative_path, line=node.lineno, column=node.col_offset + 1),
                                  note="Target resolution is not attempted in M1."))
            def visit_Call(self, node):
                label = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
                if label:
                    target = f"callref:{label}"
                    if not any(n.id == target for n in nodes):
                        nodes.append(Node(id=target, kind="external", label=label, language="python",
                                          metadata={"resolution": "unresolved syntactic reference"}))
                    edges.append(Edge(source=f"file:{relative_path}", target=target, relation="calls_reference",
                                      evidence_kind="python_ast_call_syntax", confidence=0.55,
                                      location=SourceLocation(path=relative_path, line=node.lineno, column=node.col_offset + 1),
                                      note="Syntactic reference only; dynamic dispatch and target resolution are unknown."))
                self.generic_visit(node)

        Visitor().visit(tree)
        return nodes, edges, warnings
