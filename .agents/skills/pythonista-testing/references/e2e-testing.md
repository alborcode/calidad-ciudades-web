# E2E and User Journey Testing

## ALWAYS call production code, NEVER manually construct state

**Manually constructing objects bypasses the exact code path where bugs live.**

### Bad Example: Sham Test

```python
# SHAM TEST - bypasses production code
async def test_news_with_image_e2e():
    news_post = await generator.generate_news_post(...)

    # BYPASS: Manually construct what flow.py should create
    # If flow.py forgot to pass attachment, this test still passes!
    activity_event = FeedActivityEvent(
        handle="test",
        activity_type="post",
        activity_id=FeedActivityEvent.generate_id(),
        timestamp=datetime.now(UTC),
        text=news_post.description,
        payload_json=news_post.to_json(),
        attachments=[news_post.attachment],  # WE added this, flow.py forgot!
    )

    await publisher.handle_event(activity_event)
    assert mock_external.called  # Test passes, Production broken
```

### Good Example: Real Test

```python
# REAL TEST - calls production code
async def test_news_with_image_e2e():
    # Call ACTUAL production code that creates the event
    await news_flow.create_news_post(flow_input)

    # Extract what was ACTUALLY published
    published_event = mock_queue.publish.call_args.kwargs["output"]

    # If news_flow.py forgot attachment, this FAILS
    assert published_event.attachments is not None

    await publisher.handle_event(published_event)
```

## ALWAYS let production code create state in fixtures

```python
# Production code creates initial state
@pytest_asyncio.fixture
async def initialized_sink(real_db_client):
    sink = create_sink(db_client=real_db_client)
    await sink.pre_run()  # This is what production does
    return sink

async def test_initial_state_exists(initialized_sink):
    result = await list_states()
    # Now actually testing that sink.pre_run() creates state correctly
    assert any(i.handle == INITIAL_HANDLE for i in result.items)

# Test creates what it should test for
async def test_initial_state_exists():
    await update_configuration(INITIAL_HANDLE, config)  # BYPASS
    result = await list_states()
    assert any(i.handle == INITIAL_HANDLE for i in result.items)  # Always passes!
```

## E2E Self-Check Questions

Before considering an E2E test complete, answer:

- **"If I comment out the line that passes this parameter, does any test fail?"**
- **"Did I manually construct any object that production code should create?"**
- **"If production code forgot to pass a field, would my test catch it?"**
- **"Am I executing real library code flow, or mocking it?"**

If any answer is wrong, the test is a sham.

## ALWAYS document E2E tests

```python
@pytest.mark.asyncio
async def test_news_flow_to_external_e2e():
    """
    E2E test: news_flow.create_news_post() -> Queue -> Publisher -> External

    SUT: news_flow.create_news_post(), Publisher

    Library code executed (NOT mocked):
    - news_flow.create_news_post()
    - ActivityEvent construction
    - Publisher._handle_activity_event()

    Mocked external systems:
    - LLM chains - expensive, non-deterministic
    - Search API - external API
    - External service - external dependency

    Infrastructure:
    - Queue: FakeProducer (captures messages)
    """
```

**Why document**:
- Clarifies what's tested vs mocked
- Documents integration boundaries
- Helps debug failures
- Prevents accidental over-mocking

## ALWAYS write user journey tests for new parameters

**Why**: All component tests pass while integration is broken.

When adding a parameter, trace the complete path:

```python
async def test_model_flows_from_config_to_chain():
    """
    INVARIANT: model in FlowConfig reaches ComposingChain.

    Journey: FlowConfig -> gather_sources() -> FlowInput -> ComposingChain
    """
    # User sets model (entry point)
    config = FlowConfig(model=ModelChoice.GROK_4)

    # Call production code
    result = await generator.gather_sources(configuration=config)

    # Verify at intermediate checkpoint
    assert result.model == ModelChoice.GROK_4

    # Verify at final destination
    with patch.object(ComposingChain, '__init__', return_value=None) as mock_init:
        await compose_flow.fn(result)
        mock_init.assert_called_with(model_override="grok-4")
```

## ALWAYS start E2E tests from USER's entry point

```python
# Start from user entry point
async def test_complete_generation_flow():
    # USER's entry point: configuration
    config = FlowConfig(
        sources=["https://techcrunch.com"],
        model=ModelChoice.GPT_4,
    )

    # Flow from start to finish
    await orchestrator_flow.fn(config)

    # Verify end result
    published = mock_queue.publish.call_args.kwargs["output"]
    assert published.activity_type == "post"

# Start from intermediate function
async def test_generation():
    # Not the user's entry point!
    flow_input = FlowInput(...)
    await compose_flow.fn(flow_input)
```

## Examples

### Good: Complete data flow test
```python
async def test_moderation_result_flows_to_db():
    """
    E2E: Moderator -> Queue -> Sink -> Database

    Verifies that moderation results reach persistent storage.
    """
    moderator = Moderator(channel_id="test_channel")

    # Generate result (start of flow)
    result = await moderator.check_content(frame_data)

    # Publish to queue
    await producer.publish(result, topic=TOPIC)

    # Process through sink
    sink = Sink(db_client=real_db_client)
    await sink.consume_messages()

    # Verify in database (end of flow)
    from_db = await get_latest_result(channel_id="test_channel")
    assert from_db.user_id == result.user_id
    assert from_db.details.classification == result.details.classification
```

### Good: Parameter journey test
```python
async def test_schedule_flows_from_config_to_scheduler():
    """
    INVARIANT: schedule from Config reaches Scheduler.

    Journey: Config -> create_campaign() -> Campaign -> scheduler.schedule()
    """
    config = CampaignConfig(
        campaign_id="welcome_series",
        schedule={"cron": "0 9 * * *"},  # 9 AM daily
    )

    campaign = await create_campaign(config)
    assert campaign.schedule == {"cron": "0 9 * * *"}

    with patch.object(Scheduler, 'schedule') as mock_schedule:
        await deploy_campaign(campaign)
        mock_schedule.assert_called_once()
        assert mock_schedule.call_args.kwargs["cron"] == "0 9 * * *"
```

### Bad: Manual state construction
```python
# SHAM TEST
async def test_external_receives_post():
    # Manually construct what should come from flow
    activity = {
        "actor": "user:test",
        "verb": "post",
        "object": "news:123",
        "foreign_id": "news:123",
        "attachments": [...],  # We added this manually
    }

    await external_client.add_activity(activity)
    # Test passes even if flow.py forgot to add attachments!
```
