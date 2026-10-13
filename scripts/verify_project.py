"""Validate actual file contents instead of declaring readiness from file presence."""

import ast
from pathlib import Path

import nbformat
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for directory in ["src", "tests", "scripts"]:
        for path in (ROOT / directory).rglob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for filename in ["run_full_pipeline.py", "setup.py"]:
        ast.parse((ROOT / filename).read_text(encoding="utf-8"), filename=filename)
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
    settings = yaml.safe_load((ROOT / "config/config.yaml").read_text())
    assert (ROOT / settings["data"]["raw_file"]).is_file(), "Configured raw dataset is missing"
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert isinstance(workflow.get("jobs"), dict), "CI must define executable jobs"
    for path in (ROOT / "sql").rglob("*.sql"):
        assert "[código" not in path.read_text(), f"SQL placeholder found: {path}"
    print("Python, notebook, configuration and workflow structure checks passed.")
    print("Use pytest and a pipeline run to verify behavior; PostgreSQL checks need TEST_DATABASE_URL.")


if __name__ == "__main__":
    main()
