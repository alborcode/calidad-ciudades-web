# LLM Tooling for Code Review

## Why Use External LLM Tools?

Claude Code has a 25K context limit per tool call. For reviewing entire PR diffs (which can be 50K-200K+ tokens), you need models with larger context windows.

**Benefits of full-diff review:**
1. **Cross-file pattern detection** - See duplication across files in one pass
2. **Architectural issues** - Understand how changes fit together
3. **Different perspectives** - Different models catch different issues
4. **Speed** - One comprehensive pass vs file-by-file review

## Setup: Simon Willison's LLM Tool

[llm](https://llm.datasette.io/) is a well-regarded open source CLI for interacting with LLMs.

### Installation

```bash
# Install the tool
pip install llm

# Or with pipx (recommended for CLI tools)
pipx install llm
```

### Configure a Model

**OpenAI (GPT-4, etc.):**
```bash
llm keys set openai
# Paste your API key when prompted
```

**Anthropic Claude:**
```bash
pip install llm-claude-3
llm keys set claude
# Paste your API key when prompted
```

**Google Gemini:**
```bash
pip install llm-gemini
llm keys set gemini
```

**Local models (Ollama):**
```bash
pip install llm-ollama
# Requires Ollama running locally
```

### Verify Setup

```bash
# List available models
llm models

# Test with a simple prompt
echo "Hello" | llm

# Test with specific model
echo "Hello" | llm -m gpt-4o
echo "Hello" | llm -m claude-3-sonnet
```

## Using the Review Scripts

### 1. Extract Changes

```bash
# PR: current branch vs main
./extract-changes.sh

# Specific commit
./extract-changes.sh abc123

# Path pattern (fuzzy matching)
./extract-changes.sh auth/login
./extract-changes.sh user-service  # matches user_service too
```

This creates:
- `/tmp/diff-src.txt` - Production code changes
- `/tmp/diff-tests.txt` - Test code changes
- `/tmp/review-mode.txt` - Metadata about the review

### 2. Run Code Review

```bash
# Default model
./llm-review.sh

# Specific model
./llm-review.sh -m gpt-4o
./llm-review.sh -m claude-3-5-sonnet-latest
./llm-review.sh -m gemini-1.5-pro
```

### 3. Run Test Review

```bash
./llm-review-tests.sh
./llm-review-tests.sh -m gpt-4o
```

### 4. Run Type Review

```bash
./llm-review-types.sh
./llm-review-types.sh -m claude-3-5-sonnet-latest
```

## Recommended Workflow

### Quick PR Review

```bash
# 1. Extract the diff
./extract-changes.sh

# 2. Get high-level review from a large-context model
./llm-review.sh -m gpt-4o

# 3. Use findings as hints for Claude to investigate deeper
# Copy specific issues to Claude and ask for detailed fixes
```

### Multi-Model Review

Different models catch different issues:

```bash
./extract-changes.sh

# GPT-4 for general patterns
./llm-review.sh -m gpt-4o > review-gpt4.txt

# Claude for nuanced analysis
./llm-review.sh -m claude-3-5-sonnet-latest > review-claude.txt

# Compare findings
diff review-gpt4.txt review-claude.txt
```

### Type-Focused Review

```bash
./extract-changes.sh
./llm-review-types.sh -m gpt-4o

# Then ask Claude to fix the identified type issues
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SRC_DIR` | `src/` | Source code directory |
| `TEST_DIR` | `tests/` | Test code directory |
| `OUTPUT_DIR` | `/tmp` | Where to write extracted diffs |
| `LLM_MODEL` | (llm default) | Default model for reviews |

Example:
```bash
SRC_DIR=lib/ TEST_DIR=spec/ ./extract-changes.sh
```

## Integrating with Claude Code

The LLM review provides **hints**, not final answers. Use it to:

1. **Identify areas to investigate** - "LLM flagged duplication in auth/ - let me look"
2. **Get a second opinion** - Different models may catch different issues
3. **Review large PRs quickly** - Full context in one pass
4. **Validate your own review** - Cross-check your findings

Then use Claude Code to:
- Dive deeper into flagged issues
- Implement actual fixes
- Write tests for identified problems
- Refactor based on recommendations

## Model Recommendations

| Use Case | Recommended Models |
|----------|-------------------|
| Large PRs (100+ files) | `gpt-4o`, `claude-3-5-sonnet-latest`, `gemini-1.5-pro` |
| Quick review | `gpt-4o-mini`, `claude-3-haiku` |
| Type analysis | `gpt-4o` (good at patterns) |
| Test review | `claude-3-5-sonnet-latest` (nuanced) |
| Cost-sensitive | `gpt-4o-mini`, local Ollama models |

## Troubleshooting

### "llm: command not found"
```bash
pip install llm
# or ensure ~/.local/bin is in PATH
```

### "No API key configured"
```bash
llm keys set openai  # or claude, gemini, etc.
```

### "Rate limited"
Use a different model or wait. Consider local models for high-volume use.

### "Context too long"
The scripts automatically exclude lock files. For very large PRs:
```bash
# Review src only, skip tests
OUTPUT_DIR=/tmp ./extract-changes.sh
./llm-review.sh  # Only reviews /tmp/diff-src.txt
```

## References

- [llm documentation](https://llm.datasette.io/)
- [llm-claude-3 plugin](https://github.com/simonw/llm-claude-3)
- [Available llm plugins](https://llm.datasette.io/en/stable/plugins/directory.html)
