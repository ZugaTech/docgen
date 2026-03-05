from docgen.scanner.base import PatchResult, GeneratedDoc

class JSPatcher:
    def patch(self, filepath: str, items: list[GeneratedDoc]) -> PatchResult:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        patched = 0
        items_sorted = sorted(items, key=lambda x: x.item.line_start, reverse=True)
        
        for doc in items_sorted:
            idx = doc.item.line_start - 1
            if idx < len(lines):
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                indent_str = " " * indent
                
                doc_lines = [f'{indent_str}/**\n']
                for dl in doc.docstring.splitlines():
                    doc_lines.append(f'{indent_str} * {dl}\n')
                doc_lines.append(f'{indent_str} */\n')
                
                lines.insert(idx, "".join(doc_lines))
                patched += 1
                
        new_source = "".join(lines)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_source)
            
        return PatchResult(filepath, patched, "diff-preview")
