import os
from pathlib import Path
from docgen.scanner.js_scanner import JSScanner

def test_js_scanner_identifies_undocumented():
    scanner = JSScanner()
    fixture_dir = Path(__file__).parent / "fixtures"
    
    items = scanner.scan(str(fixture_dir))
    js_items = [i for i in items if i.filepath.endswith("sample_undocumented.js")]
    
    names = [i.name for i in js_items]
    
    assert "undocumentedMethod" in names
    assert "undocumentedFunction" in names
    assert "arrowFunc" in names
    assert "JSSample" in names
    
    assert "documentedMethod" not in names
    assert "documentedFunction" not in names
