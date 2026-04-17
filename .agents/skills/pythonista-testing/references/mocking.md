# Mocking Strategy

## ALWAYS use patch.object, NEVER patch with string paths

```python
# Correct - refactor-safe
@patch.object(MyClass, 'method_name')
def test_with_mock(mock_method): ...

# Wrong - breaks silently on refactor
@patch('module.path.MyClass.method_name')
def test_with_mock(mock_method): ...
```

**Why**: `patch.object` is explicit, refactor-safe, and catches errors at test definition time.

## ALWAYS mock dependencies, NEVER mock the SUT

**System Under Test (SUT) = the code you're testing. Mock its dependencies, not the SUT itself.**

```python
# Mock dependencies, test orchestration logic
generator = NewsPostGenerator()
generator._queries_chain = AsyncMock()      # Dependency - mock it
generator._search_engine = AsyncMock()       # Dependency - mock it
await generator.generate_news_post(...)      # SUT - actually runs

# Mocking the SUT tests nothing
generator = AsyncMock(spec=NewsPostGenerator)  # Tests nothing!
```

### When mocking IS correct

Testing that coordinator handles failure correctly:
```python
# Testing coordinator logic
coordinator = WorkflowCoordinator()
coordinator.step1 = AsyncMock(return_value=success)
coordinator.step2 = AsyncMock(side_effect=ValueError("failed"))
coordinator.step3 = AsyncMock()

await coordinator.execute()

# Verify COORDINATOR LOGIC: skipped step 3 after step 2 failed
coordinator.step3.assert_not_called()
```

### When mocking is WRONG

Mocking what you're trying to test:
```python
# Testing NewsPostGenerator but mocking its core method
generator = NewsPostGenerator()
generator.generate_news_post = AsyncMock(return_value=fake_post)  # Testing nothing!
```

### Self-check

"If I mock this, what behavior am I still testing?"
- Answer is "mock call counts" -> you're testing nothing
- Answer is "coordination/orchestration logic" -> mocking is correct

## NEVER mock infrastructure - create testable wrappers

```python
# Patching logger tests implementation, not behavior
@patch("loguru.logger.warning")
def test_staleness_logging(mock_warning):
    convert_to_state(result)
    assert mock_warning.called  # So what?

# Testable wrapper in production code
def log_staleness_warning(user_id: str, age_seconds: float) -> None:
    logger.warning(f"Result became stale: {user_id}", extra={...})

# Test the wrapper
@patch.object(conversion_module, "log_staleness_warning")
def test_staleness_logging(mock_log):
    convert_to_state(result)
    assert mock_log.call_args.kwargs["user_id"] == "test_user_456"
```

**Why create wrappers**:
- Tests behavior, not implementation
- Makes production code more testable
- Documents intent with function name
- Can assert on meaningful parameters

**When to create wrappers**:
- Logging calls (logger.info, logger.warning)
- Database connections
- Metrics/observability (statsd, datadog)
- Audit events

## ALWAYS use explicit .args and .kwargs

```python
# Clear and explicit
flow_input = call_args.args[0]
delay = call_args.kwargs["delay"]

# Cryptic - requires knowing Mock internal structure
flow_input = call_args[0][0]
delay = call_args[1]["delay"]
```

**Why**: Explicit access is self-documenting and easier to debug.

## Examples

### Good: Mock dependencies
```python
@patch.object(SearchEngine, 'search', new_callable=AsyncMock)
async def test_generator_uses_search_results(mock_search):
    mock_search.return_value = ["result1", "result2"]

    generator = NewsPostGenerator()
    post = await generator.generate_news_post(...)

    # Test that generator USED the search results
    assert "result1" in post.content or "result2" in post.content
```

### Bad: Mock the SUT
```python
@patch.object(NewsPostGenerator, 'generate_news_post', new_callable=AsyncMock)
async def test_generator(mock_generate):
    mock_generate.return_value = FakePost()

    generator = NewsPostGenerator()
    post = await generator.generate_news_post(...)

    # What are we testing? Nothing! We mocked the method we're calling.
    assert post is not None  # Always True with our mock
```

### Good: Mock external services
```python
@patch.object(ExternalClient, 'add_activity', new_callable=AsyncMock)
async def test_publisher_sends_to_external(mock_add_activity):
    publisher = FeedActivitiesPublisher()
    await publisher.handle_event(test_event)

    # Verify publisher sent correct data
    assert mock_add_activity.called
    activity = mock_add_activity.call_args.args[0]
    assert activity['actor'] == test_event.user_id
```

### Good: Test wrapper functions
```python
# Production code
def report_action(action: str, entity_id: str, severity: str) -> None:
    """Log and metric for action."""
    logger.info(f"Action: {action}", extra={
        "entity_id": entity_id,
        "severity": severity,
    })
    statsd.increment(f"action.{action}.{severity}")

# Test code
@patch.object(action_module, "report_action")
def test_handler_reports_action(mock_report):
    handler.handle_inappropriate_content(...)

    mock_report.assert_called_once_with(
        action="remove",
        entity_id="entity_123",
        severity="high",
    )
```
