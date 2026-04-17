# Concurrency Testing

## ALWAYS use real infrastructure with asyncio.gather

**Why**: Mocking timing doesn't test real race conditions.

```python
async def test_concurrent_version_creation(real_db_client, clean_db):
    """Test optimistic locking under real concurrency."""
    api1 = LibraryAPI(db_client=real_db_client)
    api2 = LibraryAPI(db_client=real_db_client)

    # Real concurrent operations - one wins, other retries
    results = await asyncio.gather(
        api1._create_item_version("item__test", data1, user_id="user1"),
        api2._create_item_version("item__test", data2, user_id="user2"),
    )

    # Both succeed with different versions
    assert results[0].version != results[1].version
    assert {results[0].version, results[1].version} == {2, 3}
```

**What this tests**:
- Real race conditions
- Optimistic locking
- Retry logic
- Database transaction behavior

## NEVER use sleeps or timing tricks to test async state logic

**Why**: `asyncio.sleep()`, Events with delays, and timing-based tests are flaky, slow, and test the wrong thing.

### Bad: Using sleeps (flaky, slow)

```python
# WRONG - Using sleeps to create race conditions
async def test_queues_during_loading_WRONG(controller):
    load_event = asyncio.Event()

    async def blocking_method(*args, **kwargs):
        await load_event.wait()  # Block until signaled
        return await original_method(*args, **kwargs)

    controller.service.get_data = blocking_method

    # Start load, sleep to let it start, then act
    load_task = asyncio.create_task(controller.load())
    await asyncio.sleep(0.01)  # Timing assumption - flaky!

    result = await controller.handle_action()
    # ...
```

**Problems**:
- Flaky: timing assumptions may not hold
- Slow: accumulates across test suite
- Wrong: tests timing, not logic

### Good: Directly set state

```python
# CORRECT - Directly set state to test logic
async def test_queues_during_loading_CORRECT(controller):
    # Initialize to get initial state
    await controller.initialize()

    # Directly set state to LOADING (simulating a load in progress)
    controller.state.state = PageState.LOADING

    # Test the logic: what happens when action is called during LOADING?
    result = await controller.handle_action()

    # Assert the invariant: action should be queued, not ignored
    assert result.deferred == True
    assert len(controller.pending_commands) == 1
```

**What we're testing**: The *logic* - "when state == LOADING, actions should queue"
**NOT testing**: Race conditions, timing, or actual concurrent loads

## When timing IS needed

### Real race conditions
Use `asyncio.gather` with real infrastructure:
```python
async def test_concurrent_writes(real_db):
    results = await asyncio.gather(
        write_data(real_db, data1),
        write_data(real_db, data2),
    )
```

### Network delays
Use `@pytest.mark.timeout` for slow operations:
```python
@pytest.mark.timeout(30)
async def test_slow_network_operation():
    result = await fetch_from_slow_api()
```

## When to directly set state

- State machine transitions
- Guard conditions (is_loading, is_ready, etc.)
- Queueing logic
- Any "what if we're in state X?" test

## NEVER skip testing critical functionality

If testing seems hard, use real infrastructure instead of giving up:

```python
# Use real MongoDB for concurrency tests
@pytest_asyncio.fixture
async def real_mongodb_client():
    """In-memory MongoDB for real concurrent operations."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    yield client
    await client.drop_database("test_db")

# Use asyncio.gather for real concurrency
async def test_concurrent_operations(real_mongodb_client):
    results = await asyncio.gather(
        operation1(real_mongodb_client),
        operation2(real_mongodb_client),
    )
```

**Available real infrastructure**:
- `real_mongodb_client` fixture - in-memory MongoDB
- `asyncio.gather` - real concurrent operations
- Realistic fakes when real infra unavailable

## Examples

### Good: Test optimistic locking

```python
async def test_optimistic_locking_prevents_lost_updates(real_mongodb_client):
    """Test that concurrent updates use optimistic locking correctly."""
    collection = real_mongodb_client[DB][COLLECTION]

    # Insert initial document with version=1
    await collection.insert_one({"_id": "item1", "value": 0, "version": 1})

    async def update_with_retry(new_value):
        for _ in range(3):
            doc = await collection.find_one({"_id": "item1"})
            result = await collection.update_one(
                {"_id": "item1", "version": doc["version"]},
                {"$set": {"value": new_value, "version": doc["version"] + 1}}
            )
            if result.modified_count > 0:
                return True
            await asyncio.sleep(0.001)  # Brief retry delay
        return False

    # Concurrent updates
    results = await asyncio.gather(
        update_with_retry(100),
        update_with_retry(200),
    )

    # Both should succeed (with retries)
    assert all(results)

    # Final version should be 3 (1 + 2 updates)
    final = await collection.find_one({"_id": "item1"})
    assert final["version"] == 3
```

### Good: Test state machine logic without timing

```python
async def test_action_deferred_during_loading():
    """Test that actions are deferred when state is LOADING."""
    controller = MyController()
    await controller.initialize()

    # Directly set to LOADING state
    controller.state.state = PageState.LOADING

    # Try to perform action
    result = await controller.perform_action("update_data")

    # Action should be deferred, not executed
    assert result.status == ActionStatus.DEFERRED
    assert len(controller.pending_actions) == 1
    assert controller.pending_actions[0].name == "update_data"
```

### Good: Test concurrent data processing

```python
async def test_concurrent_message_processing(real_queue_client):
    """Test that concurrent message processing maintains order per partition."""
    processor = MessageProcessor()

    # Create messages for same partition
    messages = [
        Message(partition=0, offset=i, value=f"msg{i}")
        for i in range(10)
    ]

    # Process concurrently
    results = await asyncio.gather(
        *[processor.process(msg) for msg in messages]
    )

    # All should succeed
    assert all(r.success for r in results)

    # Check ordering was maintained per partition
    processed_offsets = processor.get_processed_offsets(partition=0)
    assert processed_offsets == list(range(10))
```

### Bad: Using timing tricks

```python
# WRONG - Flaky timing-based test
async def test_debouncing_WRONG():
    calls = []

    async def debounced_func():
        calls.append(datetime.now())

    # Call rapidly
    await debounced_func()
    await debounced_func()
    await asyncio.sleep(0.01)  # Flaky!
    await debounced_func()

    await asyncio.sleep(0.5)  # Flaky!
    assert len(calls) == 1  # Assumes exact timing
```
