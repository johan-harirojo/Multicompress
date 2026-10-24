from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseEngine(ABC):
    """Common interface for all compression engines."""

    @abstractmethod
    def compress_file(self, source: str | Path, destination: str | Path | None = None, **kwargs) -> Path:
        raise NotImplementedError

    @abstractmethod
    def decompress_file(self, source: str | Path, destination: str | Path | None = None, **kwargs) -> Path:
        raise NotImplementedError

    def test_file(self, source: str | Path, **kwargs) -> bool:
        try:
            self.decompress_file(source, **kwargs)
        except Exception:
            return False
        return True
