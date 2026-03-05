import json
from docgen.scanner.base import UndocumentedItem

def get_prompt(item: UndocumentedItem, format: str) -> str:
    return f"""
Generate a top-level {item.language} {format} format docstring for the following {item.item_type} `{item.name}`.
Ensure you return a JSON object with two keys: `docstring` (a string containing the raw docstring without markdown backticks) and `confidence` (a float between 0 and 1).

Source Code context:
```
{item.source_code}
```
"""
