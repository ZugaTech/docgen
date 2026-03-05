import os
import tempfile
from pathlib import Path
from docgen.scanner.base import UndocumentedItem, GeneratedDoc
from docgen.patcher.python_patcher import PythonPatcher
from docgen.patcher.js_patcher import JSPatcher

def test_python_patcher():
    patcher = PythonPatcher()
    
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tf:
        tf.write("def test_func():\n    pass\n")
        tf_name = tf.name
        
    item = UndocumentedItem(
        filepath=tf_name,
        line_start=1,
        line_end=2,
        name="test_func",
        item_type="function",
        source_code="def test_func():\n    pass",
        existing_docstring=None,
        language="python"
    )
    doc = GeneratedDoc(item=item, docstring="Test docstring", format="google", confidence=1.0)
    
    patcher.patch(tf_name, [doc])
    
    with open(tf_name, "r") as f:
        patched_src = f.read()
        
    os.remove(tf_name)
    assert '""""\n    Test docstring\n    """' in patched_src or '"""\n    Test docstring\n    """' in patched_src

def test_js_patcher():
    patcher = JSPatcher()
    
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as tf:
        tf.write("function testFunc() {\n    return true;\n}\n")
        tf_name = tf.name
        
    item = UndocumentedItem(
        filepath=tf_name,
        line_start=1,
        line_end=3,
        name="testFunc",
        item_type="function",
        source_code="function testFunc() {\n    return true;\n}",
        existing_docstring=None,
        language="javascript"
    )
    doc = GeneratedDoc(item=item, docstring="Test JSDoc", format="jsdoc", confidence=1.0)
    
    patcher.patch(tf_name, [doc])
    
    with open(tf_name, "r") as f:
        patched_src = f.read()
        
    os.remove(tf_name)
    assert "/**\n * Test JSDoc\n */\nfunction testFunc()" in patched_src
