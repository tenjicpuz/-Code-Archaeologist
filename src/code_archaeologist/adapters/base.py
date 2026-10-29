from pathlib import Path
from typing import Protocol
from code_archaeologist.models import Node, Edge

class LanguageAdapter(Protocol):
    name: str
    extensions: tuple[str, ...]
    def analyze_file(self, path: Path, relative_path: str) -> tuple[list[Node], list[Edge], list[str]]:
        ...
