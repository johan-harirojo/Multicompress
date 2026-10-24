from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any


@dataclass
class OperationStats:
    source_name: str
    output_name: str
    source_size: int
    output_size: int
    elapsed_seconds: float
    operation: str
    status: str = "ok"

    @property
    def gain_bytes(self) -> int:
        return self.source_size - self.output_size

    @property
    def reduction_percent(self) -> float:
        if self.source_size == 0:
            return 0.0
        return 100.0 * (self.source_size - self.output_size) / self.source_size

    @property
    def throughput_bytes_per_second(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.source_size / self.elapsed_seconds

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "output_name": self.output_name,
            "source_size": self.source_size,
            "output_size": self.output_size,
            "gain_bytes": self.gain_bytes,
            "reduction_percent": self.reduction_percent,
            "elapsed_seconds": self.elapsed_seconds,
            "throughput_bytes_per_second": self.throughput_bytes_per_second,
            "operation": self.operation,
            "status": self.status,
        }


def format_stat_line(stats: OperationStats) -> str:
    return (
        f"source={stats.source_name} output={stats.output_name} "
        f"source_size={stats.source_size} output_size={stats.output_size} "
        f"gain={stats.gain_bytes} reduction={stats.reduction_percent:.2f}% "
        f"elapsed={stats.elapsed_seconds:.3f}s throughput={stats.throughput_bytes_per_second:.0f}B/s status={stats.status}"
    )


def measure_time() -> float:
    return perf_counter()
