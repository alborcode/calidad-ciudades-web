# Intent Documentation and Testability

Guidelines for documenting design intent, extracting testable code, and writing meaningful tests.

## Core Principles

1. **Document intent at the SOURCE** where data is created, not just where it's consumed
2. **Use function design to enforce invariants** - exclude parameters that shouldn't be modified
3. **Extract pure functions** from infrastructure-heavy methods to enable testing without mocks
4. **Consolidate duplicated logic** into shared functions with documentation
5. **Test behavior** (inputs -> outputs), never implementation details (signatures, internal state)
6. **Never write sham tests** - tests that mock constructors and manually set state test the mock, not production code
7. **Document field semantics** (e.g., "handle" vs "display name") to prevent misunderstanding

---

## 1. Document Intent at the SOURCE

**ALWAYS document the "why" where data is created or transformed, not just where it's consumed.**

When data flows through multiple layers, reviewers see the consumer code first and may not understand the design. Document at the source to prevent confusion.

```python
# BAD: Documentation only at consumer
# models.py (consumer)
def normalize_user_id(value: str) -> str:
    """Normalize user IDs."""  # WHY? What's preserved?
    if value.endswith("_special"):
        return "special_participant"
    return value

# GOOD: Documentation at both source AND consumer
# agent.py (SOURCE)
# When a special condition occurs, we create a separate track.
# We append "_special" to user_id and user_name to distinguish this track.
# These display fields are normalized to "special_participant" in the
# API so the frontend doesn't show specials as separate users.
# The real user identity is preserved in real_user_id for analytics/auditing.
user_id, user_name = apply_special_suffix(user_id, user_name, is_special)

# models.py (consumer)
def normalize_user_id(value: str) -> str:
    """
    Normalize special user IDs/names to a generic placeholder for display.

    Note: Real identity is preserved in real_user_id (set at source).
    See agent.py for the full design rationale.
    """
```

---

## 2. Use Function Design to Enforce Invariants

**Design function signatures to make invalid states impossible, rather than testing for them.**

If a value should never be modified, don't accept it as a parameter. This is stronger than any test.

```python
# BAD: Function accepts real_user_id, requires discipline to not modify it
def apply_special_suffix(user_id, user_name, real_user_id, is_special):
    if is_special:
        user_id = f"{user_id}_special"
        user_name = f"{user_name}_special"
        # real_user_id must NOT be modified... but nothing prevents it
    return user_id, user_name, real_user_id

# GOOD: Function cannot modify real_user_id because it doesn't accept it
def apply_special_suffix(user_id, user_name, is_special) -> tuple[str, str]:
    """
    IMPORTANT: real_user_id is intentionally excluded - caller must pass it through
    unchanged to preserve identity for analytics/auditing.
    """
    if is_special:
        return f"{user_id}_special", f"{user_name}_special"
    return user_id, user_name
```

The design enforces the invariant - no test needed.

---

## 3. Extract Pure Functions for Testability

**Extract business logic from infrastructure-heavy methods into pure functions.**

Complex methods that depend on external systems (databases, APIs, message queues) are hard to test. Extract the logic into pure functions that take inputs and return outputs.

```python
# BAD: Logic embedded in method requiring infrastructure
class TranscriptAgent:
    async def handle_transcript(self, ...):
        user_id = self._processed_participant.identity
        user_name = self._processed_participant_username
        real_user_id = self._processed_participant.attributes.get("real_user_id")

        # Logic buried in infrastructure method - untestable without mocking everything
        if self._processed_publication.source == TrackSource.SPECIAL_AUDIO:
            user_name = f"{user_name}_special"
            user_id = f"{user_id}_special"

# GOOD: Extract pure function, call it from infrastructure method
def apply_special_suffix(user_id: str, user_name: str, is_special: bool) -> tuple[str, str]:
    """Pure function - easily testable."""
    if is_special:
        return f"{user_id}_special", f"{user_name}_special"
    return user_id, user_name

class TranscriptAgent:
    async def handle_transcript(self, ...):
        user_id = self._processed_participant.identity
        user_name = self._processed_participant_username
        is_special = self._processed_publication.source == TrackSource.SPECIAL_AUDIO
        user_id, user_name = apply_special_suffix(user_id, user_name, is_special)
```

The pure function can be tested with simple parametrized tests - no mocks needed.

---

## 4. Consolidate Duplicated Logic

**Extract duplicated code into shared functions with clear documentation.**

Duplicated code obscures intent. When the same logic appears in multiple places, extract it into a single function with documentation explaining the design.

```python
# BAD: Same validator duplicated 4 times
class User(BaseModel):
    @field_validator("user_id")
    def normalize(cls, v):
        if v.endswith("_special"):
            return "special_participant"
        return v

class AvatarDescriptor(BaseModel):
    @field_validator("user_id")
    def normalize(cls, v):  # Same code, no shared documentation
        if v.endswith("_special"):
            return "special_participant"
        return v

# GOOD: Single shared function with documentation
def normalize_special_user_id(value: str | None) -> str | None:
    """
    Normalize special user IDs to a generic placeholder for display.

    Design rationale: [explanation]
    """
    if value and value.endswith("_special"):
        return "special_participant"
    return value

class User(BaseModel):
    @field_validator("user_id")
    @classmethod
    def _normalize_user_id(cls, v: str) -> str:
        return normalize_special_user_id(v) or v
```

---

## 5. Test Behavior, Not Implementation

**Test what goes in and comes out. Don't test signatures, internal state, or implementation details.**

```python
# BAD: Testing function signature (implementation detail)
def test_real_user_id_not_in_signature():
    sig = inspect.signature(apply_special_suffix)
    assert "real_user_id" not in sig.parameters  # Tests implementation, not behavior

# GOOD: Test behavior with parametrized inputs/outputs
@pytest.mark.parametrize("user_id,user_name,is_special,expected_id,expected_name", [
    ("alice", "alice", True, "alice_special", "alice_special"),
    ("alice", "alice", False, "alice", "alice"),
])
def test_special_suffix_behavior(user_id, user_name, is_special, expected_id, expected_name):
    result_id, result_name = apply_special_suffix(user_id, user_name, is_special)
    assert result_id == expected_id
    assert result_name == expected_name
```

---

## 6. Avoid Sham Tests

**Tests that mock constructors and manually set internal state test the mock setup, not production code.**

```python
# BAD: Sham test - mocks __init__, manually sets state
@patch.object(TranscriptAgent, "__init__", return_value=None)
def test_identity_preserved(mock_init):
    agent = TranscriptAgent()
    # Manually setting state that production code should create
    agent._processed_publication = MagicMock()
    agent._processed_publication.source = TrackSource.SPECIAL_AUDIO
    agent._processed_participant = MagicMock()
    agent._processed_participant.identity = "alice"
    agent._processed_participant.attributes = {"real_user_id": "real_alice"}

    # This tests our mock setup, not production code
    # If production code changes, this test still passes!

# GOOD: Test the extracted pure function directly
def test_special_suffix_applied():
    user_id, user_name = apply_special_suffix("alice", "alice", is_special=True)
    assert user_id == "alice_special"
    assert user_name == "alice_special"
```

---

## 7. Document Field Semantics

**Document what fields mean, not just what they contain.**

```python
# BAD: Field name doesn't convey semantics
class User(BaseModel):
    user_name: str  # What format? Handle? Display name?

# GOOD: Document semantics
class User(BaseModel):
    user_name: str  # Handle format [a-zA-Z0-9_]+ for @mentions, not display name
```

This prevents bugs like using spaces in handles (`" Special"` vs `"_special"`).

---

## Summary Checklist

Before completing a feature:

- [ ] Is the design intent documented at the SOURCE where data is created?
- [ ] Are invariants enforced by function design (excluded parameters) rather than discipline?
- [ ] Is business logic extracted into pure functions that can be tested without mocks?
- [ ] Is duplicated logic consolidated into shared functions with documentation?
- [ ] Do tests verify behavior (inputs -> outputs), not implementation details?
- [ ] Are there any sham tests that mock constructors and manually set state?
- [ ] Are field semantics documented (format, purpose, constraints)?
