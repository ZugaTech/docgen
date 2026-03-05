from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from docgen.scanner.base import GeneratedDoc
import typer
import tempfile
import os
import subprocess

console = Console()

def interactive_review(docs: list[GeneratedDoc]) -> list[GeneratedDoc]:
    approved = []
    skipped = 0
    edited = 0
    
    for doc in docs:
        console.print(f"[bold cyan]File:[/bold cyan] {doc.item.filepath}:{doc.item.line_start}")
        console.print(f"[bold cyan]Item:[/bold cyan] {doc.item.name} ({doc.item.item_type})")
        
        src_syntax = Syntax(doc.item.source_code, "python" if doc.item.language == "python" else "javascript", theme="monokai")
        doc_syntax = Syntax(doc.docstring, "markdown", theme="monokai")
        
        console.print(Panel(src_syntax, title="Source Code"))
        console.print(Panel(doc_syntax, title=f"Generated Docstring (Confidence: {doc.confidence*100:.1f}%)"))
        
        choice = Prompt.ask("[bold yellow]Action[/bold yellow]", choices=["a", "e", "s", "q"], default="a", show_choices=True)
        choice = choice.lower()
        
        if choice == "q":
            break
        elif choice == "s":
            skipped += 1
            continue
        elif choice == "e":
            editor = os.environ.get("EDITOR", "nano")
            with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as tf:
                tf.write(doc.docstring)
                tf.flush()
                tf_name = tf.name
            
            subprocess.call([editor, tf_name])
            
            with open(tf_name, "r") as tf:
                doc.docstring = tf.read().strip()
            
            os.remove(tf_name)
            approved.append(doc)
            edited += 1
        elif choice == "a":
            approved.append(doc)
            
    console.print("\n[bold]Review Summary:[/bold]")
    console.print(f"Accepted: {len(approved)-edited}")
    console.print(f"Skipped: {skipped}")
    console.print(f"Edited: {edited}")
    console.print(f"Total to patch: {len(approved)}")
    
    return approved
