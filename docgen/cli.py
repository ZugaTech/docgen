import typer
import asyncio
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from docgen.config import load_config
from docgen.scanner.python_scanner import PythonScanner
from docgen.scanner.js_scanner import JSScanner
from docgen.generator.openai_generator import OpenAIGenerator
from docgen.patcher.python_patcher import PythonPatcher
from docgen.patcher.js_patcher import JSPatcher
from docgen.interactive import interactive_review

app = typer.Typer(help="docgen: automatically scan and generate docstrings via AI")
console = Console()
config = load_config()

def get_scanners(lang: str):
    if lang == "python":
        return [PythonScanner()]
    elif lang == "js":
        return [JSScanner()]
    else:
        return [PythonScanner(), JSScanner()]

def get_patcher(lang: str):
    if lang == "python":
        return PythonPatcher()
    else:
        return JSPatcher()

@app.command()
def config_init():
    """Write a default .docgenrc.toml to current directory."""
    with open(".docgenrc.toml", "w") as f:
        f.write('''format = "google"
exclude_patterns = ["tests/", "node_modules/", "venv/"]
skip_private = true
model = "gpt-4o"
language = "auto"
''')
    console.print("[green]Created .docgenrc.toml[/green]")

@app.command()
def scan(path: str, lang: str = "auto"):
    """Scan directory and print report of undocumented items."""
    scanners = get_scanners(lang)
    items = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Scanning codebase...", total=None)
        for scanner in scanners:
            items.extend(scanner.scan(path, config.exclude_patterns, config.skip_private))
        progress.update(task, completed=100)
    
    table = Table(title=f"Undocumented Items in {path}")
    table.add_column("File", style="cyan")
    table.add_column("Line", justify="right", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Has Doc", justify="center")

    for item in items:
        table.add_row(item.filepath, str(item.line_start), item.name, item.item_type, "No")

    console.print(table)
    console.print(f"Total: {len(items)} undocumented items found.")

@app.command()
def generate(
    path: str,
    format: str = typer.Option(config.format, "--format"),
    lang: str = typer.Option(config.language, "--lang"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
    exclude: List[str] = typer.Option([], "--exclude"),
    model: str = typer.Option(config.model, "--model"),
    api_key: str = typer.Option(None, "--api-key", envvar="OPENAI_API_KEY")
):
    """Scan, generate docstrings computationally, and write/review."""
    scanners = get_scanners(lang)
    items = []
    
    excludes = config.exclude_patterns + list(exclude)
    
    with Progress() as progress:
        scan_task = progress.add_task("[cyan]Scanning codebase...", total=100)
        for scanner in scanners:
            items.extend(scanner.scan(path, excludes, config.skip_private))
        progress.update(scan_task, completed=100)
        
    if not items:
        console.print("[yellow]No undocumented items found.[/yellow]")
        return
        
    generator = OpenAIGenerator(api_key=api_key)
    generated_docs = []
    
    async def generate_all():
        with Progress() as progress:
            gen_task = progress.add_task("[green]Generating docstrings...", total=len(items))
            for item in items:
                doc = await generator.generate_docstring(item, format, model)
                generated_docs.append(doc)
                progress.update(gen_task, advance=1)
                
    asyncio.run(generate_all())
    
    if dry_run:
        console.print("[yellow]Dry run: printing generated docs only.[/yellow]")
        for d in generated_docs:
            console.print(f"--- {d.item.filepath} : {d.item.name} ---")
            console.print(d.docstring)
        return
        
    if yes:
        approved_docs = generated_docs
    else:
        approved_docs = interactive_review(generated_docs)
        
    if not approved_docs:
        console.print("[yellow]No docs approved. Exiting.[/yellow]")
        return
        
    python_docs = [d for d in approved_docs if d.item.language == "python"]
    js_docs = [d for d in approved_docs if d.item.language == "javascript"]
    
    if python_docs:
        patcher = get_patcher("python")
        files = {d.item.filepath for d in python_docs}
        for f in files:
            docs = [d for d in python_docs if d.item.filepath == f]
            patcher.patch(f, docs)
            
    if js_docs:
        patcher = get_patcher("js")
        files = {d.item.filepath for d in js_docs}
        for f in files:
            docs = [d for d in js_docs if d.item.filepath == f]
            patcher.patch(f, docs)
            
    console.print(f"[green]Successfully patched {len(approved_docs)} items![/green]")

if __name__ == "__main__":
    app()
