# docgen-ai

A command-line application that scans local project code, identifies undocumented functions and classes and uses OpenAI's API to generate accurate docstrings. Supports Python and JS/TS.

## How it works
1. **Scan**: Parses your codebase and extracts undocumented functions/classes.
2. **Generate**: Prompts an LLM with code context to generate documentation according to your preferred format.
3. **Review**: Presents an interactive Typer/Rich TUI for approval or modification.
4. **Patch**: Losslessly injects the new docstrings back into your source code.

## Installation
```bash
pip install docgen-ai
```

## Quickstart
Initialize configuration:
```bash
docgen config init
```

Generate docs for your project:
```bash
docgen generate./src/ --format google --lang auto
```

Scan without generating:
```bash
docgen scan./src/
```

## Supported formats
- google (Python)
- numpy (Python)
- sphinx (Python)
- jsdoc (JavaScript/TypeScript)