import os
import subprocess
import sys


def test_help_command():
    result = subprocess.run(
        [sys.executable, "-m", "multicompress", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "multicompress" in result.stdout.lower()


def test_bzip2_cli_round_trip(tmp_path):
    source = tmp_path / "example.txt"
    source.write_text("Commission de test CLI\n" * 20, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "multicompress",
            "bzip2",
            "compress",
            str(source),
            "--keep",
        ],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0, result.stderr
    assert (source.parent / "example.txt.bz2").exists()
