# Pydantic Patterns

## External System Integration

**When writing to or reading from external systems (MongoDB, APIs, Redis, etc.), ALWAYS use Pydantic models.**

### The Problem with Raw Dicts

Raw dicts bypass Pydantic's field aliasing and serialization, leading to subtle bugs.

### Real-World Bug Example

```python
# WRONG - Using raw dict in MongoDB upsert
async def update_config(community_handle: str, config: CampaignConfiguration):
    config_data = config.model_dump()  # Gets Python field names
    now = datetime.now(timezone.utc)

    await collection.update_one(
        {"community_handle": community_handle},
        {
            "$set": {
                "drip_campaign_configuration": config_data,
                "updated_at": now,  # Wrong field name!
            },
            "$setOnInsert": {
                "created_at": now,  # Wrong field name!
            },
        },
        upsert=True,
    )
    # Result: Document has created_at/updated_at, but model expects "timestamp"
    # Later validation: ValidationError: Field required [type=missing] 0.timestamp

# CORRECT - Use Pydantic model with proper serialization
async def update_config(community_handle: str, config: CampaignConfiguration):
    config_data = config.model_dump(by_alias=True)  # Uses field aliases
    now = datetime.now(timezone.utc)

    new_state = CommunityInsightState(
        community_handle=community_handle,
        timestamp=now,  # Correct field name
        drip_campaign_configuration=config,
    )

    await collection.update_one(
        {"community_handle": community_handle},
        {
            "$set": {
                "drip_campaign_configuration": config_data,
                "timestamp": now,  # Correct field name from model
            },
            "$setOnInsert": new_state.model_dump(
                by_alias=True,
                exclude={"drip_campaign_configuration", "timestamp"}
            ),
        },
        upsert=True,
    )
```

## Key Lessons

1. **Write**: Use `model.model_dump(by_alias=True)` to serialize with correct field names
2. **Read**: Use `Model.model_validate(data)` to validate and parse external data
3. **Upserts**: Create model instances for `$setOnInsert` to ensure all fields are correct
4. **Never trust raw dicts**: External systems don't validate - Pydantic does

## Writing to External Systems

```python
# WRONG - Manual dict construction
await mongodb.insert_one({
    "user_id": user_id,
    "created_at": now,
    "metadata": {"foo": "bar"}
})

# CORRECT - Use Pydantic model
class UserRecord(BaseModel):
    user_id: str
    created_at: datetime
    metadata: dict[str, str]

record = UserRecord(user_id=user_id, created_at=now, metadata={"foo": "bar"})
await mongodb.insert_one(record.model_dump(by_alias=True))
```

## Reading from External Systems

```python
# WRONG - Using raw dict from MongoDB
doc = await mongodb.find_one({"_id": doc_id})
user_id = doc["user_id"]  # No validation, could be missing/wrong type
timestamp = doc["timestamp"]  # Might be "created_at" in DB, causing KeyError

# CORRECT - Validate through Pydantic
doc = await mongodb.find_one({"_id": doc_id})
if doc is None:
    raise HTTPException(status_code=404)

record = UserRecord.model_validate(doc)
user_id = record.user_id  # Type-safe, validated
timestamp = record.created_at  # Correct field name via alias
```

## Benefits

1. **Field aliasing works**: `timestamp` in Python -> `timestamp` in MongoDB
2. **Validation at boundaries**: Catch field mismatches when reading/writing
3. **Type safety**: IDE autocomplete, type checker catches errors
4. **Single source of truth**: Model defines structure, external system mirrors it
5. **Prevents regressions**: Tests using models catch serialization bugs

## When This Matters Most

- **Database upserts**: `$setOnInsert` must have correct field names
- **API responses**: External APIs may have different field names (use `Field(alias=...)`)
- **Message queues**: Kafka, RabbitMQ messages should validate on read
- **Cache systems**: Redis data should round-trip through models
- **Third-party APIs**: GetStream, Stripe, etc. - validate responses

## The Golden Rule

**If data crosses a system boundary (DB, API, queue, cache), it must go through a Pydantic model.**

## Common Patterns

### Field Aliasing

```python
class UserRecord(BaseModel):
    user_id: str
    created_at: datetime = Field(alias="createdAt")  # JS naming convention

    model_config = ConfigDict(populate_by_name=True)

# Can create with either name
record = UserRecord(user_id="123", created_at=now)
record = UserRecord(user_id="123", createdAt=now)

# Serialize with alias for external system
data = record.model_dump(by_alias=True)  # {"user_id": "123", "createdAt": "..."}
```

### Validation on Boundaries

```python
class APIResponse(BaseModel):
    status: str
    data: list[UserRecord]

# Validate API response
response = await httpx_client.get("/users")
validated = APIResponse.model_validate(response.json())

# Now you have type-safe data
for user in validated.data:
    print(user.user_id)  # IDE knows this is str
```

### Model Evolution

```python
class UserRecord(BaseModel):
    user_id: str
    email: str
    # New field with default - backwards compatible
    display_name: str | None = None

# Old documents without display_name still validate
old_doc = {"user_id": "123", "email": "test@example.com"}
record = UserRecord.model_validate(old_doc)  # Works!
```
