# Contributing to agent-benchmark

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/your-org/agent-benchmark
cd agent-benchmark
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests must pass before submitting a PR. Tests use `unittest.mock.patch` to
mock `time.perf_counter` — **do not add tests that actually sleep or wait**.

## Guidelines

- **Zero dependencies** — the library must remain dependency-free at runtime.
- **Type hints** everywhere in `src/`.
- **Docstrings** for all public classes and methods.
- Write tests for every new feature or bug fix.
- Keep commits atomic and descriptive.

## Pull Request Process

1. Fork the repo and create a feature branch.
2. Add/update tests.
3. Run `python -m pytest tests/ -v` — all green.
4. Open a PR with a clear description.

## Code of Conduct

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md).
