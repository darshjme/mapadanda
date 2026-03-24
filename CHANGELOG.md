# Changelog

All notable changes to **agent-benchmark** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-24

### Added
- `Benchmark` class — run a callable N times with warmup and collect timing stats
- `BenchmarkResult` — full statistical summary (mean, p50, p95, p99, std, min, max)
- `ComparisonResult` — side-by-side A/B comparison with winner and speedup ratio
- `@benchmark` decorator — zero-config timing for any function
- Regression detection via `BenchmarkResult.regression_vs(baseline, threshold)`
- Zero runtime dependencies; uses only `time.perf_counter` from stdlib
- 29 pytest tests with mocked perf_counter for fast, deterministic CI
