# safe_gather Implementation

If you don't have `safe_gather` in your codebase, here's a reference implementation:

```python
import asyncio
from typing import Any, Coroutine

async def safe_gather(
    *coros: Coroutine[Any, Any, Any],
    return_exceptions: bool = False,
    timeout: float | None = None,
) -> list[Any]:
    """
    Gather coroutines with fail-fast behavior and optional timeout.

    Unlike asyncio.gather:
    - Cancels remaining tasks on first exception (unless return_exceptions=True)
    - Supports timeout with automatic cleanup
    - Handles cancellation more gracefully

    Args:
        *coros: Coroutines to run concurrently
        return_exceptions: If True, return exceptions as results instead of raising
        timeout: Optional timeout in seconds

    Returns:
        List of results in the same order as input coroutines

    Raises:
        First exception from any coroutine (if return_exceptions=False)
        asyncio.TimeoutError if timeout exceeded
    """
    if timeout is not None:
        return await asyncio.wait_for(
            _safe_gather_impl(*coros, return_exceptions=return_exceptions),
            timeout=timeout,
        )
    return await _safe_gather_impl(*coros, return_exceptions=return_exceptions)


async def _safe_gather_impl(
    *coros: Coroutine[Any, Any, Any],
    return_exceptions: bool = False,
) -> list[Any]:
    tasks = [asyncio.create_task(coro) for coro in coros]

    if return_exceptions:
        return await asyncio.gather(*tasks, return_exceptions=True)

    try:
        return await asyncio.gather(*tasks)
    except Exception:
        # Cancel remaining tasks on failure
        for task in tasks:
            if not task.done():
                task.cancel()
        # Wait for cancellation to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
```

## Usage Examples

### Fail-fast (default)

```python
# If any task fails, remaining tasks are cancelled immediately
results = await safe_gather(
    fetch_user(user_id),
    fetch_permissions(user_id),
    fetch_settings(user_id),
)
```

### Partial results

```python
# Exceptions returned as values, not raised
results = await safe_gather(
    *[process_item(item) for item in items],
    return_exceptions=True,
)

successes = [r for r in results if not isinstance(r, Exception)]
failures = [r for r in results if isinstance(r, Exception)]
```

### With timeout

```python
# Timeout applies to entire operation
try:
    results = await safe_gather(*tasks, timeout=30.0)
except asyncio.TimeoutError:
    logger.error("Operation timed out")
```

### Cleanup with timeout

```python
# Don't wait forever for cleanup
await safe_gather(
    db.close(),
    cache.close(),
    queue.close(),
    return_exceptions=True,
    timeout=10.0,
)
```
