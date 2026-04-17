---
name: pythonista-typing
description: Python type annotations and Pydantic best practices. Use when working with types, models, or data structures. Triggers on "type", "types", "typing", "Pydantic", "BaseModel", "dict", "list", "tuple", "annotation", "hint", "Any", "TypedDict", "dataclass", "model", "schema", or when defining function signatures or data models.
---

# Type Annotations and Pydantic Best Practices

## Core Philosophy

**Use Pydantic models for structured data. Use specific types everywhere. Never use `Any` or raw dicts when structure is known.**

## Type Annotations

### Modern Python Syntax

```python
# CORRECT - Modern Python 3.9+ syntax
def process_data(items: list[str]) -> dict[str, list[int]]:
    results: dict[str, list[int]] = {}
    return results

# WRONG - Old style imports
from typing import Dict, List, Tuple
def process_data(items: List[str]) -> Dict[str, List[int]]:
    ...
```

### NEVER Use Float as Dict Keys

```python
# WRONG - Float precision issues
def group_by_duration(participants) -> dict[float, list[Participant]]:
    groups[1.5] = [p1, p2]
    return groups

# CORRECT - Use Pydantic model
class DurationGroup(BaseModel):
    duration_seconds: float
    participants: list[Participant]

def group_by_duration(participants) -> list[DurationGroup]:
    return [DurationGroup(duration_seconds=1.5, participants=[p1, p2])]
```

### Complex Return Types Must Be Named

```python
# WRONG - Unreadable
def execute_moderation(
    participants: list[Participant],
) -> tuple[BatchResults, dict[str, Optional[Egress]]]:
    pass

# CORRECT - Named model
class ModerationResult(BaseModel):
    batch_results: BatchResults
    egress_statuses: dict[str, Optional[Egress]]

def execute_moderation(participants: list[Participant]) -> ModerationResult:
    pass
```

**Rule of thumb**: If you can't read the type annotation out loud in one breath, it needs a named model.

### Always Type ALL Parameters

```python
# WRONG - Untyped callback
async def execute_moderation(
    channel_id: str,
    result_enricher=None,  # NO TYPE HINT!
):
    pass

# CORRECT - Use Protocol for callbacks
class ResultEnricher(Protocol):
    def __call__(self, result: VideoModerationResult) -> VideoModerationResult: ...

async def execute_moderation(
    channel_id: str,
    result_enricher: ResultEnricher | None = None,
):
    pass
```

### Be Specific With Collections

```python
# WRONG - What's in the list?
def get_users() -> list:
    return [{"name": "Bob"}]

# CORRECT - Specific types
def get_users() -> list[User]:
    return [User(name="Bob")]
```

### NEVER Use hasattr/getattr as Type Substitutes

```python
# WRONG - Type cop-out
def process(obj: Any):
    if hasattr(obj, "name"):
        return obj.name
    return None

# CORRECT - Use Protocol
class Named(Protocol):
    name: str

def process(obj: Named) -> str:
    return obj.name
```

## Data Structures

### Always Use Pydantic Models for Structured Data

```python
# WRONG - Raw dict
def get_video_result() -> dict[str, Any]:
    return {
        "is_appropriate": True,
        "confidence": 0.95,
    }

# CORRECT - Pydantic model
class VideoResult(BaseModel):
    is_appropriate: bool
    confidence: float

def get_video_result() -> VideoResult:
    return VideoResult(is_appropriate=True, confidence=0.95)
```

### TypedDict and dataclasses Are Prohibited

**NEVER use TypedDict or dataclasses without explicit authorization.**

```python
# WRONG
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int

# WRONG
from dataclasses import dataclass

@dataclass
class UserData:
    name: str
    age: int

# CORRECT - Always use Pydantic
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    age: int
```

### Tuple Rules

Tuples are acceptable ONLY for simple 2-element pairs:

```python
# CORRECT - Simple pair with type alias
CacheResult = tuple[str | None, bool]  # (value, cache_hit)

def get_from_cache(key: str) -> CacheResult:
    value = cache.get(key)
    return (value, value is not None)

# WRONG - More than 2 elements
def get_user_info() -> tuple[str, int, str, bool]:  # Use a model!
    return ("Alice", 30, "alice@example.com", True)
```

### Never Convert Models to Dicts Just to Add Fields

```python
# WRONG - Breaking type safety
async def analyze_video(...) -> dict[str, Any]:
    result = await llm.ainvoke(...)
    result_dict = result.model_dump()
    result_dict["_run_id"] = run_id  # Now everything is untyped!
    return result_dict

# CORRECT - Extend the model
class VideoModerationResult(BaseModel):
    details: VideoModerationDetails
    run_id: str | None = None

async def analyze_video(...) -> VideoModerationResult:
    details = await llm.ainvoke(...)
    return VideoModerationResult(details=details, run_id=run_id)
```

## Pydantic and External Systems

### Writing to External Systems

```python
# WRONG - Manual dict
await mongodb.insert_one({
    "user_id": user_id,
    "created_at": now,
})

# CORRECT - Pydantic model
class UserRecord(BaseModel):
    user_id: str
    created_at: datetime

record = UserRecord(user_id=user_id, created_at=now)
await mongodb.insert_one(record.model_dump(by_alias=True))
```

### Reading from External Systems

```python
# WRONG - Raw dict
doc = await mongodb.find_one({"_id": doc_id})
user_id = doc["user_id"]  # No validation

# CORRECT - Validate through Pydantic
doc = await mongodb.find_one({"_id": doc_id})
record = UserRecord.model_validate(doc)
user_id = record.user_id  # Type-safe, validated
```

## Reference Files

For detailed patterns:
- [references/pydantic-patterns.md](references/pydantic-patterns.md) - Pydantic patterns and external system integration

## Related Skills

- For testing typed code, see `/pythonista-testing`
- For code review, see `/pythonista-reviewing`
