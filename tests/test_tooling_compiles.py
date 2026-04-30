import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_python_tools_compile() -> None:
    tool_files = sorted((ROOT / "tools").glob("*.py"))

    assert len(tool_files) >= 5
    for path in tool_files:
        py_compile.compile(str(path), doraise=True)
