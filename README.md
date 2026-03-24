# agent-benchmark

**Performance benchmarking for LLM agents.** Timed runs with warmup, statistical summaries (mean/p50/p95/p99/std), A/B comparison, and regression detection — zero dependencies.

```
pip install agent-benchmark
```

---

## Quick Start

```python
from agent_benchmark import Benchmark

def my_agent_call():
    # simulate work
    import time; time.sleep(0.01)

b = Benchmark("gpt-4o-mini", warmup=3, runs=20)
result = b.run(my_agent_call)
print(result.summary())
# [gpt-4o-mini] runs=20 mean=10.12ms p50=10.09ms p95=10.48ms p99=10.51ms std=0.15ms min=9.98ms max=10.55ms
```

---

## Regression Detection

Did your last refactor make the agent slower? Catch it automatically:

```python
from agent_benchmark import Benchmark

def v1_agent():
    import time; time.sleep(0.050)   # baseline: ~50ms

def v2_agent():
    import time; time.sleep(0.060)   # new version: ~60ms (20% slower)

b = Benchmark("regression-check", warmup=2, runs=10)

baseline = b.run(v1_agent)
current  = b.run(v2_agent)

if current.regression_vs(baseline, threshold=0.10):
    print(f"🚨 REGRESSION DETECTED! {current.mean_ms:.1f}ms vs baseline {baseline.mean_ms:.1f}ms")
    print(f"   Slowdown: {(current.mean_ms - baseline.mean_ms) / baseline.mean_ms * 100:.1f}%")
else:
    print("✅ No regression — within threshold")
```

Output:
```
🚨 REGRESSION DETECTED! 60.3ms vs baseline 50.1ms
   Slowdown: 20.3%
```

---

## A/B Comparison

```python
from agent_benchmark import Benchmark

b = Benchmark("model-compare", warmup=3, runs=15)
comp = b.compare(v1_agent, v2_agent, name_a="GPT-4o-mini", name_b="Claude-Haiku")

print(f"Winner: {comp.winner}")
print(f"Speedup: {comp.speedup:.2f}x faster")
print(comp.result_a.summary())
print(comp.result_b.summary())
```

---

## @benchmark Decorator

```python
from agent_benchmark import benchmark

# Single-call timing
@benchmark
def fetch_context(query: str):
    ...

fetch_context("what is RAG?")
# [benchmark] fetch_context took 12.847ms

# Multi-run stats
@benchmark(runs=20)
def embed_text(text: str):
    ...

embed_text("hello world")
# [embed_text] runs=20 mean=3.21ms p50=3.18ms p95=3.45ms ...
```

---

## API Reference

### `Benchmark(name, warmup=3, runs=10)`

| Method | Returns | Description |
|--------|---------|-------------|
| `run(func, *args, **kwargs)` | `BenchmarkResult` | Run with warmup + timed iterations |
| `compare(func_a, func_b, name_a, name_b)` | `ComparisonResult` | Side-by-side benchmark |

### `BenchmarkResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `mean_ms` | float | Arithmetic mean latency |
| `median_ms` | float | p50 latency |
| `p95_ms` | float | 95th percentile latency |
| `p99_ms` | float | 99th percentile latency |
| `std_ms` | float | Standard deviation |
| `min_ms` | float | Minimum observed latency |
| `max_ms` | float | Maximum observed latency |

| Method | Description |
|--------|-------------|
| `is_faster_than(other)` | True if `self.mean_ms < other.mean_ms` |
| `regression_vs(baseline, threshold=0.10)` | True if >10% slower than baseline |
| `summary()` | One-line human-readable string |
| `to_dict()` | Serialize to dict (JSON-friendly) |

### `ComparisonResult`

| Property/Method | Description |
|-----------------|-------------|
| `winner` | `"A"` or `"B"` — lower mean wins |
| `speedup` | How many times faster the winner is |
| `to_dict()` | Full serialization including nested results |

---

## Design Principles

- **Zero dependencies** — only `time.perf_counter` from stdlib
- **High-resolution timing** — `perf_counter` has sub-microsecond resolution
- **Warmup by default** — avoids cold-start JIT/cache effects skewing results
- **Statistical rigor** — p95/p99 catch tail latency that mean misses
- **Regression-first** — `regression_vs()` is the primary CI integration point

---

## License

MIT
