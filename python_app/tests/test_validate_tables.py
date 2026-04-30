import re
import subprocess
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]


def test_validate_tables_script_passes():
    completed = subprocess.run(
        [sys.executable, "validate_tables.py"],
        cwd=APP_DIR,
        text=True,
        capture_output=True,
        check=False,
    )

    output = completed.stdout + completed.stderr
    failing_lines = [
        line for line in output.splitlines()
        if re.match(r"^(X|FAIL|FAILED)\b", line)
    ]

    assert completed.returncode == 0, output
    assert "=== VALIDATION COMPLETE ===" in output, output
    assert "Traceback (most recent call last)" not in output, output
    assert not failing_lines, "\n".join(failing_lines)
