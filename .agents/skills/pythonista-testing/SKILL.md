---
name: pythonista-testing
description: Use when writing or modifying tests, fixing bugs with TDD, reviewing test code. Triggers on "test", "tests", "testing", "TDD", "test-driven", "pytest", "add tests", "write tests", "unit test", "integration test", "test coverage", "bug fix", "fix bug", "mock", "fixture", "assert", "conftest", "parametrize", "async test", or when editing files in tests/ directory.
---

# Python Testing Best Practices

## Core Philosophy

**Write invariant-based tests that verify what SHOULD be true, not bug-affirming tests that prove bugs existed.**

## Test-Driven Development (TDD)

**ALWAYS use TDD when fixing bugs:**

1. Find existing tests for the broken functionality
2. Run them to verify they pass (shouldn't catch bug)
3. Improve tests until they fail (exposing the bug)
4. Fix the code to make tests pass
5. Verify all tests pass

## Quick Start

```bash
# Look for existing fixtures in conftest.py
# Use Claude's Grep tool: pattern="@pytest.fixture" path="tests/conftest.py"

# Look at sibling test files for patterns
ls tests/test_<module_name>/

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

## Critical Rules

### Mocking - ALWAYS use patch.object

```python
# CORRECT - refactor-safe
from unittest.mock import patch

@patch.object(MyClass, 'method_name')
def test_with_mock(mock_method):
    ...

# WRONG - breaks silently on refactor
@patch('module.path.MyClass.method_name')
def test_with_mock(mock_method):
    ...
```

### Mock Dependencies, NOT the System Under Test

```python
# CORRECT - Mock dependencies, test real code
generator = NewsPostGenerator()
generator._queries_chain = AsyncMock()      # Dependency - mock it
generator._search_engine = AsyncMock()       # Dependency - mock it
await generator.generate_news_post(...)      # SUT - actually runs

# WRONG - Tests nothing
generator = AsyncMock(spec=NewsPostGenerator)
```

### Test Data - ALWAYS use Pydantic models

```python
# CORRECT - validation, type safety
def create_test_result(channel_id: str) -> VideoModerationResult:
    return VideoModerationResult(
        channel_id=channel_id,
        user_id="test_user",
        timestamp=datetime.now(UTC),
        details=VideoModerationDetails(is_appropriate=True)
    )

# WRONG - no validation, won't catch schema changes
def create_test_data():
    return {"channel_id": "test", "user_id": "user123"}
```

### Constants - NEVER use naked literals

```python
# CORRECT - relationships explicit
DEFAULT_RECHECK_INTERVAL = 60
STALE_AGE = DEFAULT_RECHECK_INTERVAL + MODERATION_DURATION + 10

# WRONG - magic numbers
timestamp = datetime.now(UTC) - timedelta(seconds=120)  # Why 120?
```

### Invariant Testing

```python
# CORRECT - Test what SHOULD be true
def test_selector_populated_with_all_names():
    """INVARIANT: Selector contains all names from config."""
    config = make_config_with_items(["item1", "item2", "item3"])
    page = setup_page_with_config(config)
    assert page.item_selector.options == ["item1", "item2", "item3"]

# WRONG - Bug-affirming test
def test_bug_123_selector_empty():
    assert len(selector.options) > 0  # Proves bug, doesn't verify correctness
```

### E2E Testing - Call Production Code

```python
# CORRECT - Call actual production code
async def test_flow_e2e():
    await service.process_request(request_input)
    published_event = mock_queue.publish.call_args.kwargs["output"]
    assert published_event.data is not None  # Fails if code forgot data

# WRONG - Manually construct state (WE added this, not production code!)
```

### Access Mock Args Explicitly

```python
# CORRECT - Clear and explicit
flow_input = call_args.args[0]
delay = call_args.kwargs["delay"]

# WRONG - Cryptic
flow_input = call_args[0][0]
```

## Testing Checklist

Before committing:
- [ ] All imports at top of file
- [ ] Using `patch.object`, not `patch`
- [ ] Mocking dependencies, not SUT
- [ ] No mocking of model classes
- [ ] Test data uses Pydantic models
- [ ] Checked conftest.py for existing fixtures
- [ ] No naked literals - all values are constants
- [ ] Mock args accessed with `.args[N]` / `.kwargs["name"]`
- [ ] E2E tests call actual production code
- [ ] Tests verify invariants, not bug existence
- [ ] 100% coverage of new code

## Reference Files

For detailed patterns and examples:
- [references/mocking.md](references/mocking.md) - Mocking strategies and when to mock
- [references/test-data.md](references/test-data.md) - Test data creation patterns
- [references/e2e-testing.md](references/e2e-testing.md) - E2E and user journey patterns
- [references/intent-and-testability.md](references/intent-and-testability.md) - Pure functions, testability
- [references/concurrency.md](references/concurrency.md) - Async and concurrency testing
- [references/fixtures.md](references/fixtures.md) - Pytest fixtures and decorators

## Related Skills

- [/pythonista-debugging](../pythonista-debugging/SKILL.md) - Root cause analysis
- [/pythonista-typing](../pythonista-typing/SKILL.md) - Type safety in tests
- [/pythonista-async](../pythonista-async/SKILL.md) - Async testing patterns
- [/pythonista-reviewing](../pythonista-reviewing/SKILL.md) - Test code review
