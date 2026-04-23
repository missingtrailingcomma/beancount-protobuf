"""Unit tests for src/beancount2proto/main.py."""
import subprocess

BEANCOUNT_FILE_CONTENT = """
2023-01-01 open Assets:Bank:Checking
2023-12-31 close Assets:Bank:Checking
"""


def test_script_execution_directly(tmp_path):
    """Test running the script directly via the command line."""

    # 1. Create a real, temporary beancount file on disk
    dummy_ledger = tmp_path / "test.beancount"
    dummy_ledger.write_text(BEANCOUNT_FILE_CONTENT)

    # 2. Run the script as a subprocess (like typing it in the terminal)
    # sys.executable ensures we use the same python environment running pytest
    result = subprocess.run(
        ["uv", "run", "python", "-m", "src.beancount2proto.main", str(dummy_ledger)],
        capture_output=True,
        text=True,
        check=False,  # Don't raise an exception on non-zero exit, we'll check it ourselves
    )

    # 3. Assert the script ran successfully (exit code 0)
    assert result.returncode == 0

    # 4. Verify the output
    assert f"Parsing {dummy_ledger}..." in result.stdout
    assert "Successfully parsed" in result.stdout
    assert "User protobuf:" in result.stdout
