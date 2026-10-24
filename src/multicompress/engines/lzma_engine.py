from __future__ import annotations

import lzma
from pathlib import Path

from ..exceptions import CompressionError, DecompressionError, ValidationError
from ..file_utils import safe_output_path, validate_input_file
from .base import BaseEngine


class LZMAEngine(BaseEngine):
    """Wrapper around Python's stdlib lzma module."""

    _VALID_FORMATS = {"lzma", "xz", "lzma2"}

    @staticmethod
    def _resolve_compress_params(format_name: str, preset: int) -> tuple[int, list[dict[str, int | str]] | None]:
        if format_name == "lzma":
            return lzma.FORMAT_ALONE, None
        if format_name == "xz":
            return lzma.FORMAT_XZ, None
        if format_name == "lzma2":
            return lzma.FORMAT_RAW, [{"id": lzma.FILTER_LZMA2, "preset": preset}]
        raise ValueError(f"Unsupported LZMA format: {format_name}")

    @staticmethod
    def _resolve_decompress_params(source_path: Path) -> tuple[int, list[dict[str, int | str]] | None]:
        suffix = source_path.suffix.lower()
        if suffix == ".xz":
            return lzma.FORMAT_XZ, None
        if suffix == ".lzma":
            return lzma.FORMAT_ALONE, None
        if suffix == ".lzma2":
            return lzma.FORMAT_RAW, [{"id": lzma.FILTER_LZMA2}]
        return lzma.FORMAT_AUTO, None

    def compress_file(
        self,
        source: str | Path,
        destination: str | Path | None = None,
        format_name: str = "lzma",
        preset: int = 6,
        **kwargs,
    ) -> Path:
        if format_name not in self._VALID_FORMATS:
            raise ValueError(f"Unsupported LZMA format: {format_name}")
        source_path = validate_input_file(source)
        suffix = ".lzma" if format_name == "lzma" else ".xz" if format_name == "xz" else ".lzma2"
        target = safe_output_path(source_path, suffix, destination)
        format_id, filters = self._resolve_compress_params(format_name, preset)
        try:
            data = lzma.compress(source_path.read_bytes(), format=format_id, preset=preset, filters=filters)
        except Exception as exc:  # pragma: no cover - defensive
            raise CompressionError(f"LZMA compression failed for {source_path}") from exc
        try:
            target.write_bytes(data)
        except OSError as exc:
            raise CompressionError(f"Could not write compressed file: {target}") from exc
        return target

    def decompress_file(self, source: str | Path, destination: str | Path | None = None, **kwargs) -> Path:
        source_path = validate_input_file(source)
        if destination is None:
            if source_path.suffix in {".xz", ".lzma", ".lzma2"}:
                candidate = source_path.with_suffix("")
            else:
                candidate = source_path.parent / f"{source_path.name}.out"
            if candidate.exists():
                candidate = source_path.parent / f"{source_path.stem}.restored"
            target = candidate
            if target.exists():
                raise FileExistsError(f"Refusing to overwrite existing file: {target}")
        else:
            target = Path(destination)
            if target.exists():
                raise FileExistsError(f"Refusing to overwrite existing file: {target}")
        format_id, filters = self._resolve_decompress_params(source_path)
        try:
            data = lzma.decompress(source_path.read_bytes(), format=format_id, filters=filters)
        except Exception as exc:
            raise DecompressionError(f"Invalid or corrupted LZMA stream: {source_path}") from exc
        try:
            target.write_bytes(data)
        except OSError as exc:
            raise DecompressionError(f"Could not write decoded file: {target}") from exc
        return target
