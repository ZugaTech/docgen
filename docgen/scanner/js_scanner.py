import re
import pathspec
from pathlib import Path
from typing import List, Optional

from docgen.scanner.base import BaseScanner, UndocumentedItem

class JSScanner(BaseScanner):
    def scan(self, directory: str, exclude_patterns: Optional[List[str]] = None, skip_private: bool = True) -> List[UndocumentedItem]:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', exclude_patterns or [])
        items = []
        base_path = Path(directory)
        
        patterns = [
            (r'function\s+([a-zA-Z0-9_]+)\s*\(', "function"),
            (r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[a-zA-Z0-9_]+)\s*=>', "function"),
            (r'class\s+([a-zA-Z0-9_]+)', "class"),
            (r'(?:async\s+)?([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{', "method")
        ]
        
        extensions = [".js", ".jsx", ".ts", ".tsx"]
        
        for ext in extensions:
            for path in base_path.rglob(f"*{ext}"):
                if 'node_modules' in path.parts:
                    continue
                rel_path = path.relative_to(base_path)
                if spec.match_file(str(rel_path)):
                    continue
                    
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except Exception:
                    continue
                    
                for i, line in enumerate(lines):
                    for pattern, item_type in patterns:
                        match = re.search(pattern, line)
                        if match:
                            name = match.group(1)
                            # skip common keywords
                            if name in ["if", "for", "while", "else", "switch", "catch", "function", "return"]:
                                continue
                            if skip_private and name.startswith("_"):
                                continue
                            
                            # check if previous line has JSDoc
                            has_doc = False
                            for j in range(i - 1, max(-1, i - 10), -1):
                                if "*/" in lines[j] and j >= 1 and "/**" in lines[j-1]: # simplified check
                                    has_doc = True
                                    break
                                elif "/**" in lines[j]:
                                    has_doc = True
                                    break
                                elif lines[j].strip() == "":
                                    continue
                                else:
                                    break
                                    
                            if not has_doc:
                                start = i + 1
                                end = min(len(lines), i + 11)
                                src = "".join(lines[start-1:end])
                                items.append(UndocumentedItem(
                                    filepath=str(path),
                                    line_start=start,
                                    line_end=end,
                                    name=name,
                                    item_type=item_type,
                                    source_code=src,
                                    existing_docstring=None,
                                    language="javascript"
                                ))
                            break # matched one pattern
                            
        items.sort(key=lambda x: (x.filepath, x.line_start))
        return items
