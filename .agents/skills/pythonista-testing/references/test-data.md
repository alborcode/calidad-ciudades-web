# Test Data Creation

## ALWAYS use Pydantic models, NEVER dicts

```python
# Correct - validation, type safety
def create_test_result(channel_id: str) -> ModerationResult:
    return ModerationResult(
        channel_id=channel_id,
        user_id="test_user",
        timestamp=datetime.now(UTC),
        details=ModerationDetails(
            is_appropriate=True,
            classification="SAFE"
        )
    )

# Wrong - no validation, won't catch schema changes
def create_test_data():
    return {
        "channel_id": "test",
        "user_id": "user123"
    }

# Wrong - JSON strings are even worse
def create_test_data_worse():
    return json.loads('{"channel_id": "test"}')
```

**Why use model classes**:
- Type safety - catches field name typos
- Validation - catches invalid values
- Schema evolution - breaks when fields change
- Self-documenting - clear what fields are required

## NEVER use naked literals - extract constants

```python
# Correct - relationships are explicit
from myapp.models import DURATION_ESTIMATE

DEFAULT_RECHECK_INTERVAL = 60
STALE_AGE = DEFAULT_RECHECK_INTERVAL + DURATION_ESTIMATE.total_seconds() + 10

def test_staleness_detection():
    timestamp = datetime.now(UTC) - timedelta(seconds=STALE_AGE)
    result = create_test_result(timestamp=timestamp)
    assert is_stale(result)

# Wrong - where do these numbers come from?
def test_staleness_detection():
    timestamp = datetime.now(UTC) - timedelta(seconds=120)
    result = create_test_result(timestamp=timestamp)
    assert is_stale(result)  # Why 120? What's the relationship?
```

**Why extract constants**:
- Documents relationships between values
- Easy to update when business logic changes
- Self-documenting test intent
- Reduces magic numbers

## ALWAYS assert invariants early, NEVER filter None

```python
# Correct - fails fast on bad test data
for p in participants:
    assert p.user_id is not None, f"Test participant must have user_id: {p}"

user_ids = [p.user_id for p in participants]

# Wrong - silently skips bad data, hides bugs
user_ids = [p.user_id for p in participants if p.user_id is not None]
```

**Why assert early**:
- Test data problems caught immediately
- Clearer error messages
- Documents test data requirements
- Prevents tests passing for wrong reasons

## ALWAYS use TypedDict for fixtures returning dicts

```python
from typing import TypedDict

# Correct - type-safe dictionary
class FlowTaskMocks(TypedDict):
    retrieve_items: AsyncMock
    schedule: AsyncMock

@pytest.fixture
def mock_flow_tasks() -> FlowTaskMocks:
    with patch.object(module, "_retrieve_items", new_callable=AsyncMock) as mock_retrieve:
        with patch.object(module, "_schedule", new_callable=AsyncMock) as mock_schedule:
            yield {
                "retrieve_items": mock_retrieve,
                "schedule": mock_schedule,
            }

def test_flow(mock_flow_tasks: FlowTaskMocks):
    mocks["retreive_items"]  # <- Type error! Catches typo
```

**Why TypedDict**:
- Catches typos at write-time
- IDE autocomplete
- Type checker validation
- Self-documenting fixture structure

## Check tests/conftest.py for existing fixtures

Before creating new fixtures or test helpers:
```bash
# Search for existing fixtures
grep -r "@pytest.fixture" tests/conftest.py

# Look at sibling test files
ls tests/test_<module_name>/
```

## Examples

### Good: Factory function with defaults
```python
def create_test_moderation_result(
    channel_id: str = "test_channel_123",
    user_id: str = "test_user_456",
    is_appropriate: bool = True,
    classification: str = "SAFE",
) -> ModerationResult:
    """Create test ModerationResult with sensible defaults."""
    return ModerationResult(
        channel_id=channel_id,
        user_id=user_id,
        timestamp=datetime.now(UTC),
        details=ModerationDetails(
            is_appropriate=is_appropriate,
            classification=classification,
            severity="low" if is_appropriate else "high",
        )
    )
```

### Good: Constants for test timing
```python
# At top of test file
DEFAULT_TIMEOUT = 5.0
RETRY_INTERVAL = 1.0
MAX_RETRIES = 3
STALE_THRESHOLD = DEFAULT_TIMEOUT * 2

def test_operation_timeout():
    with pytest.raises(TimeoutError):
        await operation_with_timeout(timeout=DEFAULT_TIMEOUT)

def test_staleness_detection():
    age = STALE_THRESHOLD + 1  # Just over threshold
    assert is_stale(age)
```

### Good: Reusable test data builders
```python
class TestDataBuilder:
    """Builder for complex test data structures."""

    @staticmethod
    def flow_input(
        sources: list[str] | None = None,
        model: ModelChoice = ModelChoice.GPT_4,
    ) -> FlowInput:
        return FlowInput(
            handle="test_handle",
            sources=sources or ["https://example.com/news"],
            model=model,
            max_length=500,
        )

    @staticmethod
    def activity_event(
        activity_type: str = "post",
        has_attachment: bool = False,
    ) -> ActivityEvent:
        event = ActivityEvent(
            handle="test_handle",
            activity_type=activity_type,
            activity_id=ActivityEvent.generate_id(),
            timestamp=datetime.now(UTC),
            text="Test activity",
        )
        if has_attachment:
            event.attachments = [ImageAttachment(url="https://example.com/image.jpg")]
        return event
```
