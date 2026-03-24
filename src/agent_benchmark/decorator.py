"""@benchmark decorator for quick per-call or multi-run timing."""

from __future__ import annotations

import functools
import time
from typing import Any, Callable

from .core import Benchmark


def benchmark(_func: Callable | None = None, *, runs: int = 1) -> Any:
    """Decorator that times a function.

    Usage::

        @benchmark
        def my_func(): ...

        @benchmark(runs=10)
        def my_func(): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if runs == 1:
                t0 = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                print(f"[benchmark] {func.__name__} took {elapsed_ms:.3f}ms")
                return result
            else:
                b = Benchmark(name=func.__name__, warmup=0, runs=runs)
                br = b.run(func, *args, **kwargs)
                print(br.summary())
                # Return last call result by calling once more
                return func(*args, **kwargs)

        return wrapper

    if _func is not None:
        # Called as @benchmark (no parentheses)
        return decorator(_func)
    # Called as @benchmark(runs=N)
    return decorator
