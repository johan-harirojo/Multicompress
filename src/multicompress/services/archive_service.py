from __future__ import annotations

from pathlib import Path

from ..engines.sevenzip_engine import SevenZipEngine
from ..exceptions import ArchiveError, MissingDependencyError


class ArchiveService:
    def __init__(self) -> None:
        self.engine = SevenZipEngine()

    def create(self, source: str | Path, archive_path: str | Path, method: str = "LZMA2") -> str:
        return self.engine.create_archive(source, archive_path, method=method)

    def extract(self, archive_path: str | Path, destination: str | Path) -> str:
        return self.engine.extract_archive(archive_path, destination)

    def list(self, archive_path: str | Path) -> str:
        return self.engine.list_archive(archive_path)

    def test(self, archive_path: str | Path) -> bool:
        return self.engine.test_archive(archive_path)

    def validate_dependency(self) -> None:
        if not self.engine.binary:
            raise MissingDependencyError("7z missing")
