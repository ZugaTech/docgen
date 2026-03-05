import ast
import linecache
from pathlib import Path
from typing import List, Optional
import pathspec

from docgen.scanner.base import BaseScanner, UndocumentedItem

class PythonVisitor(ast.NodeVisitor):
    def __init__(self, filepath: str, skip_private: bool):
        self.filepath = filepath
        self.skip_private = skip_private
        self.items = []
        self.current_class = None

    def visit_ClassDef(self, node):
        self._check_node(node, "class")
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node):
        item_type = "method" if self.current_class else "function"
        self._check_node(node, item_type)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        item_type = "method" if self.current_class else "function"
        self._check_node(node, item_type)
        self.generic_visit(node)

    def _check_node(self, node, item_type: str):
        name = node.name
        if self.skip_private and name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
            return

        has_doc = False
        if getattr(node, "body", None):
            first_stmt = node.body[0]
            if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                has_doc = True
        
        if not has_doc:
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            src_lines = [linecache.getline(self.filepath, i) for i in range(start, end + 1)]
            src = "".join(src_lines)
            
            self.items.append(UndocumentedItem(
                filepath=self.filepath,
                line_start=start,
                line_end=end,
                name=name,
                item_type=item_type,
                source_code=src,
                existing_docstring=None,
                language="python"
            ))

class PythonScanner(BaseScanner):
    def scan(self, directory: str, exclude_patterns: Optional[List[str]] = None, skip_private: bool = True) -> List[UndocumentedItem]:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', exclude_patterns or [])
        items = []
        base_path = Path(directory)
        
        for path in base_path.rglob("*.py"):
            rel_path = path.relative_to(base_path)
            if spec.match_file(str(rel_path)):
                continue
                
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=str(path))
            except Exception:
                continue
            
            visitor = PythonVisitor(str(path), skip_private)
            visitor.visit(tree)
            items.extend(visitor.items)
            
        items.sort(key=lambda x: (x.filepath, x.line_start))
        return items
