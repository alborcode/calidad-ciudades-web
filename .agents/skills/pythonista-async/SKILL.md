---
name: pythonista-async
description: Use when writing async code, using asyncio.gather, handling concurrent operations. Triggers on "asyncio", "async", "await", "gather", "concurrent", "parallel", "fail-fast", "timeout", "race condition", "cancellation", "coroutine", "task", "CancelledError", or when writing async functions.
---

# Async Patterns

## Core Rules

1. **Prefer `safe_gather`** for all new async code - fail-fast, timeout support, cleaner cancellation
2. **Use `return_exceptions=True`** for partial-results patterns
3. **Always consider timeout** for long-running operations
4. **Don't migrate** existing cleanup code (low priority, both work fine)

## safe_gather vs asyncio.gather

**`safe_gather` is better in ALL cases** because it provides:
- Fail-fast cancellation (when not using `return_exceptions=True`)
- Timeout support with automatic cleanup
- Cleaner cancellation handling

See [references/safe-gather.md](references/safe-gather.md) for implementation.

## Pattern: All Tasks Must Succeed (fail-fast)

```python
# Initialization - all workers must start
await safe_gather(*[worker.pre_run() for worker in workers])

# Data fetching - need all pieces
channel_info, front_row, participants = await safe_gather(
    fetch_channel_info(channel_id),
    fetch_front_row(channel_id),
    fetch_participants(channel_id),
)

# With timeout
results = await safe_gather(*tasks, timeout=30.0)
```

## Pattern: Partial Results Acceptable

```python
# Use safe_gather with return_exceptions=True
results = await safe_gather(*batch_tasks, return_exceptions=True)
for result in results:
    if isinstance(result, Exception):
        logger.error(f"Task failed: {result}")
    else:
        process(result)

# With timeout
results = await safe_gather(*batch_tasks, return_exceptions=True, timeout=30.0)
```

## Pattern: Cleanup/Shutdown

```python
# With timeout for cleanup (don't wait forever)
await safe_gather(
    service1.shutdown(),
    service2.shutdown(),
    return_exceptions=True,
    timeout=10.0
)

# OK to keep existing asyncio.gather for cleanup
await asyncio.gather(*cancelled_tasks, return_exceptions=True)
```

## Migration Decision Tree

```
Is this new code?
├─ Yes -> Use safe_gather
└─ No (existing code)
   └─ Is it cleanup with return_exceptions=True?
      ├─ Yes -> Keep asyncio.gather (optional to migrate)
      └─ No -> Would fail-fast or timeout help?
         ├─ Yes -> Migrate to safe_gather
         └─ No -> Low priority
```

## Key Principles

1. **Fail-fast by default**: If one task fails, cancel the rest
2. **Always consider timeout**: Long-running operations need timeouts
3. **Clean cancellation**: Handle CancelledError properly
4. **Don't wait forever**: Especially for cleanup/shutdown

## Reference Files

- [references/safe-gather.md](references/safe-gather.md) - safe_gather implementation

## Related Skills

- [/pythonista-testing](../pythonista-testing/SKILL.md) - Testing async code
- [/pythonista-typing](../pythonista-typing/SKILL.md) - Async type annotations
- [/pythonista-debugging](../pythonista-debugging/SKILL.md) - Debugging async issues
