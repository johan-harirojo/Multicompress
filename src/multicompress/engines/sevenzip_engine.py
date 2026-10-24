from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..exceptions import ArchiveError, MissingDependencyError


class SevenZipEngine:
    """Interface to the system 7z binary, if available."""

    def __init__(self, binary: str = "7z") -> None:
        self.binary = shutil.which(binary)
        if self.binary is None:
            raise MissingDependencyError(
                "The '7z' executable is required for 7-Zip support. Install the 'p7zip' package on Arch Linux: pacman -S p7zip"
            )

    def create_archive(self, source: str | Path, archive_path: str | Path, method: str = "LZMA2") -> str:
        source_path = Path(source)
        archive = Path(archive_path)
        archive.parent.mkdir(parents=True, exist_ok=True)
        if archive.exists():
            raise FileExistsError(f"Refusing to overwrite existing archive: {archive}")
        cmd = [self.binary, "a", "-t7z", "-m", f"0={method}", "-y", str(archive), str(source_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ArchiveError(f"Failed to create archive: {result.stderr or result.stdout or 'unknown error'}")
        return str(archive)

    def extract_archive(self, archive_path: str | Path, destination: str | Path) -> str:
        archive = Path(archive_path)
        destination_path = Path(destination)
        destination_path.mkdir(parents=True, exist_ok=True)
        cmd = [self.binary, "x", str(archive), "-o" + str(destination_path), "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ArchiveError(f"Failed to extract archive: {result.stderr or result.stdout or 'unknown error'}")
        return str(destination_path)

    def list_archive(self, archive_path: str | Path) -> str:
        archive = Path(archive_path)
        cmd = [self.binary, "l", str(archive)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ArchiveError(f"Failed to list archive: {result.stderr or result.stdout or 'unknown error'}")
        return result.stdout

    def test_archive(self, archive_path: str | Path) -> bool:
        archive = Path(archive_path)
        cmd = [self.binary, "t", str(archive)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
