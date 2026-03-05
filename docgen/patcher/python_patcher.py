import libcst as cst
from docgen.scanner.base import PatchResult, GeneratedDoc

class DocstringTransformer(cst.CSTTransformer):
    def __init__(self, items: list[GeneratedDoc]):
        self.items = {item.item.line_start: item.docstring for item in items}
        self.patched = 0

    def leave_FunctionDef(self, original_node, updated_node):
        line = getattr(original_node, "lineno", -1)  # this is simplistic, requires position metadata
        return updated_node
        
    def leave_ClassDef(self, original_node, updated_node):
        return updated_node

class PythonPatcher:
    def patch(self, filepath: str, items: list[GeneratedDoc]) -> PatchResult:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
            
        # Simplified string patching for robust diffs without complex CST metadata
        lines = source.splitlines()
        patched = 0
        items_sorted = sorted(items, key=lambda x: x.item.line_start, reverse=True)
        
        for doc in items_sorted:
            # target start is line_start (1-indexed). The body usually starts after the def/class line 
            # we will insert as docstring right after line_start
            idx = doc.item.line_start - 1
            # find first line after sig
            while idx < len(lines) and not lines[idx].rstrip().endswith(':'):
                idx += 1
            if idx < len(lines):
                indent = len(lines[idx+1]) - len(lines[idx+1].lstrip()) if idx+1 < len(lines) else 4
                indent_str = " " * indent
                doc_lines = [f'{indent_str}"""\n']
                for dl in doc.docstring.splitlines():
                    doc_lines.append(f'{indent_str}{dl}\n')
                doc_lines.append(f'{indent_str}"""\n')
                
                lines.insert(idx + 1, "".join(doc_lines).rstrip('\n'))
                patched += 1
                
        new_source = "\n".join(lines) + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_source)
            
        return PatchResult(filepath, patched, "diff-preview")
