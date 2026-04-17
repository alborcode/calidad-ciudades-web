---
name: pythonista-patterning
description: Pattern discovery and code reuse for Python projects. Use when writing new code, implementing features, or refactoring. Triggers on "pattern", "reuse", "duplicate", "extract", "helper", "refactor", "architecture", "existing code", "search for", "similar", "copy", "paste", or when about to write new functionality.
---

# Pattern Discovery and Architecture Trust

## Core Philosophy

**Before writing ANY new code, actively search for existing patterns and reuse opportunities.**

Duplicating code with subtle variations is one of the most damaging things you can do to a codebase.

## The Pattern Discovery Workflow

When implementing ANY feature:

### 1. Search for Similar Implementations

```bash
# Search for related code
grep -r "similar_function" src/

# Check sibling files in same directory
ls src/services/

# Look at parallel structures
# If writing campaign_api.py, check drip_api.py, prompt_api.py
```

### 2. Document Patterns Found

- Note the common structure/approach
- Identify what varies vs what stays the same
- List helper functions or utilities used

### 3. Follow Established Patterns Exactly

- Use the same parameter names and types
- Use the same error handling approach
- Use the same validation strategy

### 4. Identify Reuse Opportunities

- Spot duplicated logic that can be extracted
- Find DB queries that appear multiple times
- Notice validation patterns repeated across files

## Balance: Don't Over-Engineer, Don't Under-Engineer

### Under-Engineering (BAD)

```python
# campaign_api.py
async def update_campaign(community_handle: str, campaign: Campaign):
    if campaign.version == 0:
        current = await collection.find_one({"community_handle": community_handle})
        next_version = (current["campaign"]["version"] + 1) if current else 1
        campaign.version = next_version

# drip_api.py - DUPLICATE with subtle variation!
async def update_drip(community_handle: str, drip: Drip):
    if drip.version == 0:
        current = await collection.find_one({"community_handle": community_handle})
        next_version = (current["drip"]["version"] + 1) if current else 1
        drip.version = next_version
```

### Over-Engineering (BAD)

```python
# Creating a generic "VersionedEntityManager" when only 2 entities need it
class VersionedEntityManager(ABC, Generic[T]):
    @abstractmethod
    async def get_current_version(self, handle: str) -> int | None: ...
    # 50+ lines of generic infrastructure for 2 use cases
```

### Right Balance (GOOD)

```python
# Simple, focused helper
async def auto_increment_version(
    collection,
    community_handle: str,
    field_name: str,
    entity: VersionedEntity,
) -> VersionedEntity:
    """Auto-increment version using version=0 sentinel."""
    if entity.version == 0:
        current = await collection.find_one({"community_handle": community_handle})
        current_version = current.get(field_name, {}).get("version", 0) if current else 0
        entity.version = current_version + 1
    return entity

# Usage
campaign = await auto_increment_version(collection, handle, "campaign", campaign)
drip = await auto_increment_version(collection, handle, "drip", drip)
```

## Simple Helper vs Infrastructure

### Simple Helper - Extract Immediately

- Duplicated calculations
- Repeated DB queries (same query in 3+ places)
- Filtering/validation logic repeated across functions
- **Action**: Extract now, include in current PR

### Infrastructure - Ask First

- Affects how multiple components interact
- Introduces new architectural layer
- Changes system structure
- **Action**: Ask user, likely separate PR

## Trust the Architecture

**NEVER duplicate validation that already exists in lower layers.**

### Wrong - Service Layer Blocks API

```python
async def _create_item(self, name, item):
    versions = await api.list_item_versions(make_id(name), include_deleted=False)
    if versions:
        raise ValueError(f"Item '{name}' already exists")  # Blocks API!
    return await api.create_library_item(item, user_id=user_id)
```

### Correct - Service Layer Trusts API

```python
async def _create_item(self, name, item):
    validate_name(name)  # Only validate what service should
    return await api.create_library_item(item, user_id=user_id)  # Let API handle versioning
```

### Before Adding Validation, Ask:

1. Does a lower layer already handle this?
2. What is this layer's responsibility?
3. Am I preventing the lower layer from doing its job?

## Merge Conflicts: Investigate Before Restoring

**ALWAYS investigate WHY code is missing before restoring it.**

```bash
# Check what exists on main
git show main:path/to/file.py | grep -A 20 "function_name"

# Check git log for related changes
git log --oneline --all -- path/to/file.py | head -20
```

### Ask These Questions

1. Was this deletion intentional?
2. What's the new way to accomplish this?
3. Why is the new approach better?
4. Are approaches complementary, competing, or extensible?

## Checklist

Before writing new code:
- [ ] Searched for existing patterns (grep, sibling files, parallel structures)
- [ ] Documented patterns found
- [ ] Following established patterns exactly
- [ ] Identified reuse opportunities
- [ ] Not duplicating validation from lower layers
- [ ] Simple helpers extracted, infrastructure changes discussed

## Related Skills

- For debugging philosophy, see `/pythonista-debugging`
- For testing patterns, see `/pythonista-testing`
- For code review, see `/pythonista-reviewing`
