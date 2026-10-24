from __future__ import annotations

import bz2
from pathlib import Path

from ..exceptions import CompressionError, DecompressionError
from ..file_utils import safe_output_path, validate_input_file
from .base import BaseEngine


class BZip2Engine(BaseEngine):
    """Wrapper around Python's stdlib bz2 module."""

    def compress_file(self, source: str | Path, destination: str | Path | None = None, level: int = 9, **kwargs) -> Path:
        source_path = validate_input_file(source)
        target = safe_output_path(source_path, ".bz2", destination)
        try:
            compressed = bz2.compress(source_path.read_bytes(), compresslevel=level)
        except Exception as exc:  # pragma: no cover - defensive
            raise CompressionError(f"Compression failed for {source_path}") from exc
        try:
            target.write_bytes(compressed)
        except OSError as exc:
            raise CompressionError(f"Could not write compressed file: {target}") from exc
        return target

    def decompress_file(self, source: str | Path, destination: str | Path | None = None, **kwargs) -> Path:
        source_path = validate_input_file(source)
        if destination is None:
            candidate = source_path.with_suffix("")
            if candidate == source_path or candidate.exists():
                candidate = source_path.parent / f"{source_path.stem}.restored"
            target = candidate
            if target.exists():
                raise FileExistsError(f"Refusing to overwrite existing file: {target}")
        else:
            target = Path(destination)
            if target.exists():
                raise FileExistsError(f"Refusing to overwrite existing file: {target}")
        try:
            data = bz2.decompress(source_path.read_bytes())
        except Exception as exc:
            raise DecompressionError(f"Invalid or corrupted BZip2 stream: {source_path}") from exc
        try:
            target.write_bytes(data)
        except OSError as exc:
            raise DecompressionError(f"Could not write decoded file: {target}") from exc
        return target
