"""Execute and save notebook outputs in-process, without starting a network kernel."""

import platform
from pathlib import Path

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    import os

    original_directory = Path.cwd()
    shell = InteractiveShell.instance()
    try:
        os.chdir(ROOT / "notebooks")
        for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
            shell.reset(new_session=True)
            notebook = nbformat.read(path, as_version=4)
            execution_count = 0
            for cell in notebook.cells:
                if cell.cell_type != "code":
                    continue
                execution_count += 1
                with capture_output(stdout=True, stderr=True, display=True) as captured:
                    result = shell.run_cell(cell.source, store_history=False)
                error = result.error_before_exec or result.error_in_exec
                if error:
                    raise RuntimeError(f"{path.name}, code cell {execution_count}: {error}") from error
                cell.execution_count = execution_count
                cell.outputs = []
                for stream, value in [("stdout", captured.stdout), ("stderr", captured.stderr)]:
                    if value:
                        cell.outputs.append(nbformat.v4.new_output("stream", name=stream, text=value))
                for rich in captured.outputs:
                    cell.outputs.append(
                        nbformat.v4.new_output("display_data", data=rich.data, metadata=rich.metadata)
                    )
            notebook.metadata.language_info = {"name": "python", "version": platform.python_version()}
            nbformat.validate(notebook)
            nbformat.write(notebook, path)
            print(f"Executed {path.name}: {execution_count} code cells, no errors")
    finally:
        os.chdir(original_directory)


if __name__ == "__main__":
    main()
