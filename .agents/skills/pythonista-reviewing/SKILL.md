---
name: pythonista-reviewing
description: Use when reviewing code, PRs, or diffs. Triggers on "review", "code review", "PR", "pull request", "diff", "check this", "look at this code", "quality", "refactor", "egregious", "cross-file", "duplicate", "duplication", or when examining code for issues.
---

# Code Review Best Practices

## Core Philosophy

**Review at PR level, not file-by-file. Focus on egregious structural issues, not minutia. Look for cross-file patterns that indicate architectural problems.**

## Quick Start

```bash
# ALWAYS filter out lock files first (often 10k+ lines of noise)
git diff main...HEAD -- . ':!uv.lock' ':!poetry.lock' > /tmp/pr-diff.txt
wc -lc /tmp/pr-diff.txt  # Most diffs fit in 256KB after this

# If still too big, filter more
git diff main...HEAD -- . ':!uv.lock' ':!docs/*' > /tmp/code-diff.txt
```

## What to Look For - Egregious Issues Only

### Quick Checklist
- [ ] **Code duplication** - Same logic in 2+ places?
- [ ] **Repeated patterns** - Same code structure 3+ times?
- [ ] **God functions** - Functions over 100 lines?
- [ ] **Weak types** - Any, object, raw dict/list, missing annotations?
- [ ] **Type-deficient patterns** - hasattr, getattr instead of proper types?
- [ ] **Meaningless tests** - Tests that just verify assignment?
- [ ] **Dead code** - Unused functions, commented code?

### What NOT to Flag
- Variable naming (unless truly confusing)
- Line length, comment style, whitespace, import order

These are auto-fixable or minor. Focus on structural problems.

## LLM-Based Full Diff Review

**Why use external LLM tools?** Claude Code has a 25K context limit per tool call. For reviewing entire PR diffs (50K-200K+ tokens), use models with larger context windows.

**Benefits:**
1. Cross-file pattern detection in one pass
2. Different models catch different issues
3. Faster than file-by-file review

### Workflow

```bash
# 1. Extract changes (handles lock file exclusion automatically)
./scripts/extract-changes.sh              # PR: current branch vs main
./scripts/extract-changes.sh abc123       # Specific commit
./scripts/extract-changes.sh auth/login   # Path pattern (fuzzy match)

# 2. Run code review with large-context model
./scripts/llm-review.sh -m gpt-4o
./scripts/llm-review.sh -m claude-3-5-sonnet-latest

# 3. Run specialized reviews
./scripts/llm-review-tests.sh -m gpt-4o      # Test quality
./scripts/llm-review-types.sh -m gpt-4o      # Type hints
```

### Setup

Requires [Simon Willison's llm tool](https://llm.datasette.io/):

```bash
pip install llm
llm keys set openai          # For GPT-4
pip install llm-claude-3     # For Claude
llm keys set claude
```

See [references/llm-tooling.md](references/llm-tooling.md) for full setup and usage guide.

### Using LLM Findings

LLM review provides **hints**, not final answers:
1. Identify areas to investigate deeper
2. Cross-check with different models
3. Use Claude Code to implement actual fixes

## Human-in-the-Loop After Code Review

**CRITICAL:** After completing a code review, ALWAYS:

1. **Present findings** - Output the full review report
2. **List suggested actions** - Number each potential fix
3. **Ask for approval** - Use AskUserQuestion before executing
4. **Wait for explicit approval** - User may reject or approve selectively

**Example flow:**
```
[Code review findings output]

## Suggested Actions
1. Add format-duration validator to Schema
2. Add tests for format-duration validation

Which items should I proceed with?
```

## Reference Files

- [references/what-to-flag.md](references/what-to-flag.md) - Duplication, weak types, god functions
- [references/code-bloat-patterns.md](references/code-bloat-patterns.md) - AI-generated bloat patterns
- [references/llm-tooling.md](references/llm-tooling.md) - LLM tool setup and usage

**Remember**: The ENTIRE POINT of full diff review is cross-file patterns. Don't chunk unless you absolutely must!

## Related Skills

- [/pythonista-testing](../pythonista-testing/SKILL.md) - Test code review
- [/pythonista-typing](../pythonista-typing/SKILL.md) - Type issues to flag
- [/pythonista-patterning](../pythonista-patterning/SKILL.md) - Pattern discovery
- [/pythonista-debugging](../pythonista-debugging/SKILL.md) - Root cause analysis
