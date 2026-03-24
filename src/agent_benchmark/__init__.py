"""agent-benchmark: Performance benchmarking for LLM agents."""

from .core import Benchmark, BenchmarkResult, ComparisonResult
from .decorator import benchmark

__all__ = ["Benchmark", "BenchmarkResult", "ComparisonResult", "benchmark"]
__version__ = "1.0.0"
