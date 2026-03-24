"""22+ pytest tests for agent-benchmark — all timing mocked via perf_counter."""

from __future__ import annotations

import sys
import time
from unittest.mock import patch, call
import pytest

sys.path.insert(0, "/tmp/agent-benchmark/src")

from agent_benchmark import Benchmark, BenchmarkResult, ComparisonResult, benchmark
from agent_benchmark.core import _percentile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(name="test", runs=10, mean=100.0, median=100.0,
                 p95=110.0, p99=120.0, std=5.0, min_ms=90.0, max_ms=130.0):
    return BenchmarkResult(
        name=name, runs=runs, mean_ms=mean, median_ms=median,
        p95_ms=p95, p99_ms=p99, std_ms=std, min_ms=min_ms, max_ms=max_ms,
    )


def _mock_perf_counter(values: list[float]):
    """Return a side_effect list for perf_counter: pairs of (start, end)."""
    it = iter(values)
    def _counter():
        return next(it)
    return _counter


# ---------------------------------------------------------------------------
# _percentile helper
# ---------------------------------------------------------------------------

def test_percentile_p50():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50) == pytest.approx(3.0)

def test_percentile_p0():
    assert _percentile([1.0, 2.0, 3.0], 0) == pytest.approx(1.0)

def test_percentile_p100():
    assert _percentile([1.0, 2.0, 3.0], 100) == pytest.approx(3.0)

def test_percentile_empty():
    assert _percentile([], 50) == 0.0

def test_percentile_single():
    assert _percentile([42.0], 99) == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# BenchmarkResult
# ---------------------------------------------------------------------------

def test_result_fields():
    r = _make_result()
    assert r.name == "test"
    assert r.runs == 10
    assert r.mean_ms == 100.0

def test_is_faster_than_true():
    fast = _make_result(mean=50.0)
    slow = _make_result(mean=100.0)
    assert fast.is_faster_than(slow) is True

def test_is_faster_than_false():
    fast = _make_result(mean=50.0)
    slow = _make_result(mean=100.0)
    assert slow.is_faster_than(fast) is False

def test_is_faster_than_equal():
    r = _make_result(mean=100.0)
    assert r.is_faster_than(_make_result(mean=100.0)) is False

def test_regression_vs_above_threshold():
    baseline = _make_result(mean=100.0)
    current = _make_result(mean=115.0)  # 15% slower
    assert current.regression_vs(baseline, threshold=0.10) is True

def test_regression_vs_below_threshold():
    baseline = _make_result(mean=100.0)
    current = _make_result(mean=105.0)  # 5% slower
    assert current.regression_vs(baseline, threshold=0.10) is False

def test_regression_vs_zero_baseline():
    baseline = _make_result(mean=0.0)
    current = _make_result(mean=50.0)
    assert current.regression_vs(baseline) is False

def test_regression_vs_faster_is_not_regression():
    baseline = _make_result(mean=100.0)
    current = _make_result(mean=80.0)  # faster
    assert current.regression_vs(baseline) is False

def test_to_dict_keys():
    r = _make_result()
    d = r.to_dict()
    assert set(d.keys()) == {"name","runs","mean_ms","median_ms","p95_ms","p99_ms","std_ms","min_ms","max_ms"}

def test_summary_contains_name():
    r = _make_result(name="mytest")
    assert "mytest" in r.summary()

def test_summary_contains_mean():
    r = _make_result(mean=123.45)
    assert "123.45" in r.summary()


# ---------------------------------------------------------------------------
# Benchmark.run with mocked perf_counter
# ---------------------------------------------------------------------------

def _build_counter_values(warmup=3, runs=10, warmup_delta=0.0, run_delta=0.05):
    """Generate perf_counter return values for the timed phase only.
    Warmup calls func() with no perf_counter; only timed runs use it.
    """
    values = []
    t = 0.0
    for _ in range(runs):
        values.append(t); t += run_delta; values.append(t)
    return values


def test_benchmark_run_correct_mean():
    # Each of 10 timed calls takes exactly 50ms = 0.05s
    counter_values = _build_counter_values(warmup=3, runs=10, run_delta=0.05)
    func = lambda: None
    b = Benchmark("x", warmup=3, runs=10)
    with patch("agent_benchmark.core.time.perf_counter", side_effect=counter_values):
        result = b.run(func)
    assert result.mean_ms == pytest.approx(50.0, rel=1e-6)


def test_benchmark_run_correct_min_max():
    # Vary run_delta: first 5 runs = 10ms, next 5 = 90ms
    # Warmup calls func() with no perf_counter calls
    values = []
    t = 0.0
    for i in range(10):
        values.append(t)
        t += 0.01 if i < 5 else 0.09
        values.append(t)
    b = Benchmark("y", warmup=3, runs=10)
    with patch("agent_benchmark.core.time.perf_counter", side_effect=values):
        result = b.run(lambda: None)
    assert result.min_ms == pytest.approx(10.0, rel=1e-4)
    assert result.max_ms == pytest.approx(90.0, rel=1e-4)


def test_benchmark_run_returns_correct_run_count():
    counter_values = _build_counter_values(warmup=2, runs=5, run_delta=0.02)
    b = Benchmark("z", warmup=2, runs=5)
    with patch("agent_benchmark.core.time.perf_counter", side_effect=counter_values):
        result = b.run(lambda: None)
    assert result.runs == 5


def test_benchmark_invalid_runs():
    with pytest.raises(ValueError, match="runs must be"):
        Benchmark("bad", runs=0)


def test_benchmark_invalid_warmup():
    with pytest.raises(ValueError, match="warmup must be"):
        Benchmark("bad", warmup=-1)


# ---------------------------------------------------------------------------
# ComparisonResult
# ---------------------------------------------------------------------------

def test_comparison_winner_a():
    ra = _make_result(name="A", mean=50.0)
    rb = _make_result(name="B", mean=100.0)
    comp = ComparisonResult(result_a=ra, result_b=rb)
    assert comp.winner == "A"

def test_comparison_winner_b():
    ra = _make_result(name="A", mean=200.0)
    rb = _make_result(name="B", mean=100.0)
    comp = ComparisonResult(result_a=ra, result_b=rb)
    assert comp.winner == "B"

def test_comparison_speedup():
    ra = _make_result(mean=50.0)
    rb = _make_result(mean=100.0)
    comp = ComparisonResult(result_a=ra, result_b=rb)
    assert comp.speedup == pytest.approx(2.0)

def test_comparison_to_dict_has_winner():
    ra = _make_result(mean=40.0)
    rb = _make_result(mean=80.0)
    comp = ComparisonResult(result_a=ra, result_b=rb)
    d = comp.to_dict()
    assert "winner" in d
    assert d["winner"] == "A"
    assert "speedup" in d

def test_comparison_equal_means_winner_a():
    ra = _make_result(mean=100.0)
    rb = _make_result(mean=100.0)
    comp = ComparisonResult(result_a=ra, result_b=rb)
    assert comp.winner == "A"  # tie → A wins


# ---------------------------------------------------------------------------
# Benchmark.compare
# ---------------------------------------------------------------------------

def test_benchmark_compare_returns_comparison_result():
    counter_values = _build_counter_values(warmup=0, runs=5, run_delta=0.01)
    counter_values2 = _build_counter_values(warmup=0, runs=5, run_delta=0.02)
    combined = counter_values + counter_values2
    b = Benchmark("cmp", warmup=1, runs=5)
    with patch("agent_benchmark.core.time.perf_counter", side_effect=combined):
        comp = b.compare(lambda: None, lambda: None, name_a="fast", name_b="slow")
    assert isinstance(comp, ComparisonResult)
    assert comp.result_a.name == "fast"
    assert comp.result_b.name == "slow"


# ---------------------------------------------------------------------------
# @benchmark decorator
# ---------------------------------------------------------------------------

def test_decorator_no_args_calls_func(capsys):
    @benchmark
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5
    out = capsys.readouterr().out
    assert "add" in out
    assert "ms" in out


def test_decorator_with_runs(capsys):
    @benchmark(runs=5)
    def noop():
        return 42

    result = noop()
    assert result == 42
    out = capsys.readouterr().out
    assert "noop" in out
