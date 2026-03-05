import os
from pathlib import Path
from docgen.scanner.python_scanner import PythonScanner

def test_python_scanner_identifies_undocumented():
    scanner = PythonScanner()
    fixture_dir = Path(__file__).parent / "fixtures"
    
    items = scanner.scan(str(fixture_dir))
    python_items = [i for i in items if i.filepath.endswith("sample_undocumented.py")]
    
    # undocumented_method, undocumented_function, PythonSample (class itself is undocumented!)
    names = [i.name for i in python_items]
    
    assert "undocumented_method" in names
    assert "undocumented_function" in names
    assert "PythonSample" in names
    
    # documented ones should not be in names
    assert "documented_method" not in names
    assert "documented_function" not in names
