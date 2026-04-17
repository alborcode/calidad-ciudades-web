---
name: pythonista-debugging
description: Use when encountering errors, bugs, or problems. Triggers on "bug", "error", "fix", "debug", "traceback", "stack trace", "exception", "crash", "broken", "not working", "failing", "issue", "workaround", "wrapper", "hack", "reproduce", "bisect", or when tempted to add complexity to avoid fixing the real problem.
---

# Debugging and Root Cause Fixing

## Core Philosophy

**Find and fix the root cause. NEVER work around problems with wrappers or complexity.**

## Debugging Workflow

### 1. Read the Stack Trace

```python
# Stack traces read bottom-to-top. The last frame is where error occurred.
Traceback (most recent call last):
  File "main.py", line 10, in <module>      # Entry point
    result = process_data(data)              # Calling function
  File "processor.py", line 25, in process_data
    return transform(item)                   # Where it failed
TypeError: 'NoneType' has no attribute 'items'  # What went wrong
```

**Key info:** File, line number, function name, actual error message.

### 2. Reproduce the Bug

```bash
# Create minimal reproduction
pytest tests/test_module.py::test_specific -v

# Or write a quick script
python -c "from module import func; func(problematic_input)"
```

### 3. Use Debugger or Print Statements

```python
# Quick debugging with print (remove after!)
print(f"DEBUG: {variable=}, {type(variable)=}")

# Better: Use debugger
import pdb; pdb.set_trace()  # Interactive debugger

# Or breakpoint() in Python 3.7+
breakpoint()
```

### 4. Bisect if Needed

```bash
# Find which commit introduced the bug
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git will guide you through testing commits
```

## The Anti-Pattern: Working Around Instead of Fixing

When you encounter an error, your instinct may be to:
1. Add a wrapper class
2. Use `__getattr__` for dynamic delegation
3. Use `# type: ignore` to suppress errors
4. Create helper classes that "adapt" interfaces

**This is WRONG.** These are signs you're working around instead of fixing.

## Common Workarounds to Avoid

### Wrapper Classes with `__getattr__`

```python
# WRONG - Magic delegation
class TestWrapper:
    def __init__(self, obj):
        self.obj = obj
    def __getattr__(self, name):
        return getattr(self.obj, name)

# CORRECT - Simple helper function
def test_helper(obj):
    pass
```

### Adapter Classes

```python
# WRONG - Adapter to hide interface mismatch
class TestAdapter:
    def __init__(self, production_obj):
        self.obj = production_obj
    def adapted_method(self):
        return self.obj.method().to_dict()

# CORRECT - Transform inline, fix the interface
def test_something(production_obj):
    result = production_obj.method()
    assert result.to_dict()["field"] == expected
```

### Type Ignores to Hide Problems

```python
# WRONG - Hiding the problem
result = maybe_none.items()  # type: ignore

# CORRECT - Handle the None case
if maybe_none is not None:
    result = maybe_none.items()
```

## Red Flags

You're working around instead of fixing if you're:

1. Creating a wrapper class "just for tests"
2. Using `__getattr__` or other magic methods
3. Adding complexity to avoid changing existing code
4. Thinking "I'll just adapt this interface..."
5. Using `# type: ignore` without investigating why

## The Right Approach

1. **Stop** when you realize you're working around
2. **Identify** the root cause (read stack trace, reproduce)
3. **Fix** the root cause with simple, explicit code
4. **Delete** any workarounds you created

## Questions to Ask

- Am I adding complexity to avoid fixing the real problem?
- Is there a simpler, more direct way to do this?
- Would someone reading this code understand what's happening?
- Can I reproduce this bug with a minimal test case?

## Related Skills

- [/pythonista-testing](../pythonista-testing/SKILL.md) - TDD for bug fixes
- [/pythonista-typing](../pythonista-typing/SKILL.md) - Type safety
- [/pythonista-patterning](../pythonista-patterning/SKILL.md) - Pattern discovery
