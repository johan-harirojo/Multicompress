from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from ..engines.bzip2_engine import BZip2Engine
from ..engines.lzma_engine import LZMAEngine
from ..exceptions import CompressionError, DecompressionError
from ..statistics import OperationStats


@dataclass
class CompressionRequest:
    format_name: str
    operation: str
    source: Path
    destination: Path | None = None
    level: int | None = None
    preset: int | None = None
    keep_source: bool = False
    force: bool = False


class CompressionService:
    def __init__(self) -> None:
        self._bzip2 = BZip2Engine()
        self._lzma = LZMAEngine()

    def compress(self, request: CompressionRequest) -> OperationStats:
        started = perf_counter()
        if request.format_name == "bzip2":
            output = self._bzip2.compress_file(request.source, request.destination, level=request.level or 9)
        elif request.format_name == "lzma":
            output = self._lzma.compress_file(request.source, request.destination, format_name=request.format_name, preset=request.preset or 6)
        else:
            raise CompressionError(f"Unsupported format: {request.format_name}")
        total_time = perf_counter() - started
        source_size = request.source.stat().st_size
        output_size = output.stat().st_size
        return OperationStats(
            source_name=str(request.source),
            output_name=str(output),
            source_size=source_size,
            output_size=output_size,
            elapsed_seconds=total_time,
            operation="compress",
            status="ok",
        )

    def decompress(self, request: CompressionRequest) -> OperationStats:
        started = perf_counter()
        if request.format_name == "bzip2":
            output = self._bzip2.decompress_file(request.source, request.destination)
        elif request.format_name == "lzma":
            output = self._lzma.decompress_file(request.source, request.destination)
        else:
            raise DecompressionError(f"Unsupported format: {request.format_name}")
        total_time = perf_counter() - started
        source_size = request.source.stat().st_size
        output_size = output.stat().st_size
        return OperationStats(
            source_name=str(request.source),
            output_name=str(output),
            source_size=source_size,
            output_size=output_size,
            elapsed_seconds=total_time,
            operation="decompress",
            status="ok",
        )
