"""Core benchmarking primitives."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


def _percentile(sorted_data: list[float], pct: float) -> float:
    """Compute percentile from a pre-sorted list."""
    if not sorted_data:
        return 0.0
    n = len(sorted_data)
    idx = (pct / 100) * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    frac = idx - lo
    return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])


@dataclass
class BenchmarkResult:
    name: str
    runs: int
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    std_ms: float
    min_ms: float
    max_ms: float

    def is_faster_than(self, other: "BenchmarkResult") -> bool:
        """Return True if this result has a lower mean than *other*."""
        return self.mean_ms < other.mean_ms

    def regression_vs(self, baseline: "BenchmarkResult", threshold: float = 0.10) -> bool:
        """Return True if this result is more than *threshold* (default 10%) slower than baseline."""
        if baseline.mean_ms == 0:
            return False
        return (self.mean_ms - baseline.mean_ms) / baseline.mean_ms > threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "runs": self.runs,
            "mean_ms": self.mean_ms,
            "median_ms": self.median_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
            "std_ms": self.std_ms,
            "min_ms": self.min_ms,
            "max_ms": self.max_ms,
        }

    def summary(self) -> str:
        return (
            f"[{self.name}] runs={self.runs} mean={self.mean_ms:.2f}ms "
            f"p50={self.median_ms:.2f}ms p95={self.p95_ms:.2f}ms "
            f"p99={self.p99_ms:.2f}ms std={self.std_ms:.2f}ms "
            f"min={self.min_ms:.2f}ms max={self.max_ms:.2f}ms"
        )


@dataclass
class ComparisonResult:
    result_a: BenchmarkResult
    result_b: BenchmarkResult

    @property
    def winner(self) -> str:
        """Return 'A' or 'B' — whoever has the lower mean."""
        return "A" if self.result_a.mean_ms <= self.result_b.mean_ms else "B"

    @property
    def speedup(self) -> float:
        """How many times faster is the winner compared to the loser."""
        a, b = self.result_a.mean_ms, self.result_b.mean_ms
        if a == 0 and b == 0:
            return 1.0
        if self.winner == "A":
            return b / a if a > 0 else float("inf")
        return a / b if b > 0 else float("inf")

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_a": self.result_a.to_dict(),
            "result_b": self.result_b.to_dict(),
            "winner": self.winner,
            "speedup": self.speedup,
        }


class Benchmark:
    """Run a callable N times with optional warmup and collect timing statistics."""

    def __init__(self, name: str, warmup: int = 3, runs: int = 10) -> None:
        if runs < 1:
            raise ValueError("runs must be >= 1")
        if warmup < 0:
            raise ValueError("warmup must be >= 0")
        self.name = name
        self.warmup = warmup
        self.runs = runs

    def run(self, func: Callable, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Execute *func* with warmup + timed runs, return BenchmarkResult."""
        # Warmup phase
        for _ in range(self.warmup):
            func(*args, **kwargs)

        # Timed phase
        timings_ms: list[float] = []
        for _ in range(self.runs):
            t0 = time.perf_counter()
            func(*args, **kwargs)
            t1 = time.perf_counter()
            timings_ms.append((t1 - t0) * 1000.0)

        sorted_t = sorted(timings_ms)
        mean = sum(timings_ms) / len(timings_ms)
        variance = sum((x - mean) ** 2 for x in timings_ms) / len(timings_ms)
        std = variance ** 0.5

        return BenchmarkResult(
            name=self.name,
            runs=self.runs,
            mean_ms=mean,
            median_ms=_percentile(sorted_t, 50),
            p95_ms=_percentile(sorted_t, 95),
            p99_ms=_percentile(sorted_t, 99),
            std_ms=std,
            min_ms=sorted_t[0],
            max_ms=sorted_t[-1],
        )

    def compare(
        self,
        func_a: Callable,
        func_b: Callable,
        name_a: str = "A",
        name_b: str = "B",
    ) -> ComparisonResult:
        """Run both functions and return a ComparisonResult."""
        original_name = self.name
        self.name = name_a
        result_a = self.run(func_a)
        self.name = name_b
        result_b = self.run(func_b)
        self.name = original_name
        return ComparisonResult(result_a=result_a, result_b=result_b)
