# Fixtures and Running Tests

## ALWAYS check conftest.py before creating fixtures

```bash
# Search for existing fixtures
grep -r "@pytest.fixture" tests/conftest.py

# Look at sibling test files for patterns
ls tests/test_<module_name>/
```

**Why check first**:
- Avoid duplicating existing fixtures
- Follow established patterns
- Reuse test data builders
- Maintain consistency

## Fixture Decorators

### @pytest.fixture for sync fixtures

```python
@pytest.fixture
def test_config():
    """Synchronous fixture."""
    return Configuration(setting="test_value")
```

### @pytest_asyncio.fixture for async fixtures

```python
@pytest_asyncio.fixture
async def initialized_service():
    """Async fixture - requires await."""
    service = MyService()
    await service.initialize()
    yield service
    await service.cleanup()
```

**Rule**: Use `@pytest.fixture` for sync, `@pytest_asyncio.fixture` ONLY for async.

## Running Tests

### Run all tests with coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Run specific test file

```bash
pytest tests/path/to/test_file.py -v
```

### Run specific test class

```bash
pytest tests/test_module/test_api.py::TestEndpoint -v
```

### Run with print statements visible

```bash
pytest -s
```

### Run tests matching pattern

```bash
pytest -k "test_moderation" -v
```

### Run with timeout for slow tests

```bash
pytest --timeout=60  # 60 second timeout per test
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input_val,expected", [
    (10, 20),
    (5, 10),
    (0, 0),
])
def test_doubling(input_val, expected):
    """Test multiple cases efficiently."""
    assert double(input_val) == expected
```

## Test Naming

```python
# Descriptive - explains what is tested
def test_latest_per_user_returns_newest_result_per_user():
    pass

def test_policy_reload_after_60_seconds():
    pass

# Vague - avoid
def test_endpoint():
    pass

def test_policy():
    pass
```

## Common Testing Patterns

### Testing API Endpoints

```python
@pytest.mark.asyncio
async def test_endpoint_returns_correct_data(app, mock_db_client, clean_db):
    # Arrange: Create test data using model classes
    test_result = ModerationResult(
        channel_id="channel_123",
        user_id="user_456",
        timestamp=datetime.now(UTC),
        details=ModerationDetails(is_appropriate=True, classification="SAFE")
    )

    collection = mock_db_client[DATABASE_NAME][COLLECTION_NAME]
    await collection.insert_one(test_result.model_dump(by_alias=True))

    # Act: Call endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/channels/channel_123/moderation")

    # Assert: Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["channel_id"] == "channel_123"
```

### Testing Business Logic with Mocks

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch.object(FeatureFlagWrapper, 'get_instance')
async def test_policy_reload(mock_instance):
    # Arrange: Setup mock
    mock_client = AsyncMock()
    mock_client.variation.return_value = {"enabled": True, "settings": {}}
    mock_instance.return_value = mock_client

    # Act: Test logic
    moderator = Moderator(channel_id="test", shared_producer=None)
    policy = await moderator._ensure_policy_loaded()

    # Assert: Verify behavior
    assert policy.enabled is True
    mock_instance.assert_called_once()
```

## Example: Complete Test File Structure

```python
"""Tests for moderation service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from myapp.models import (
    ModerationDetails,
    ModerationResult,
)
from myapp.moderator import Moderator

# Constants at top
DEFAULT_TIMEOUT = 5.0
STALE_THRESHOLD = 120.0

# Test data factories
def create_test_moderation_result(
    channel_id: str = "test_channel",
    is_appropriate: bool = True,
) -> ModerationResult:
    """Factory for test moderation results."""
    return ModerationResult(
        channel_id=channel_id,
        user_id="test_user",
        timestamp=datetime.now(UTC),
        details=ModerationDetails(
            is_appropriate=is_appropriate,
            classification="SAFE" if is_appropriate else "UNSAFE",
        )
    )

# Fixtures
@pytest_asyncio.fixture
async def moderator():
    """Create initialized moderator."""
    mod = Moderator(channel_id="test_channel")
    await mod.initialize()
    yield mod
    await mod.cleanup()

# Tests
@pytest.mark.asyncio
async def test_moderator_detects_inappropriate_content(moderator):
    """Test that moderator correctly identifies inappropriate content."""
    result = await moderator.check_content(inappropriate_frame)
    assert result.details.is_appropriate is False

@pytest.mark.asyncio
@patch.object(Moderator, '_call_ml_model', new_callable=AsyncMock)
async def test_moderator_caches_results(mock_ml_model, moderator):
    """Test that moderator caches results to reduce API calls."""
    mock_ml_model.return_value = create_test_moderation_result()

    # First call
    await moderator.check_content(frame)
    # Second call - should use cache
    await moderator.check_content(frame)

    # ML model called only once
    assert mock_ml_model.call_count == 1
```
