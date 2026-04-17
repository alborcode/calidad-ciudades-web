#!/bin/bash
# Run LLM-based code review on extracted changes
#
# Prerequisites:
#   - Simon Willison's llm tool: pip install llm
#   - A configured model: llm keys set openai / llm install llm-claude-3
#
# Usage:
#   ./llm-review.sh                    # Review with default model
#   ./llm-review.sh -m gpt-4o          # Use specific model
#   ./llm-review.sh -m claude-3-sonnet # Use Claude
#
# Environment variables:
#   LLM_MODEL       Model to use (default: from llm config)
#   GUIDELINES_DIR  Directory with guideline markdown files
#   OUTPUT_DIR      Directory with extracted diffs (default: /tmp)

set -e

OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
DIFF_SRC="$OUTPUT_DIR/diff-src.txt"
DIFF_TESTS="$OUTPUT_DIR/diff-tests.txt"
REVIEW_MODE="$OUTPUT_DIR/review-mode.txt"

# Parse arguments
MODEL_ARG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL_ARG="-m $2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Check prerequisites
if ! command -v llm &> /dev/null; then
    echo "ERROR: 'llm' tool not found."
    echo ""
    echo "Install with: pip install llm"
    echo "Then configure: llm keys set openai"
    echo "Or for Claude: pip install llm-claude-3 && llm keys set claude"
    echo ""
    echo "See: https://llm.datasette.io/"
    exit 1
fi

# Check if we have any changes to review
if [ ! -s "$DIFF_SRC" ] && [ ! -s "$DIFF_TESTS" ]; then
    echo "No code changes to review."
    echo "Run extract-changes.sh first."
    exit 0
fi

# Build the review prompt
build_prompt() {
    cat << 'PROMPT_START'
# Code Review Instructions

You are performing a code review. Focus ONLY on **EGREGIOUS issues**:

## What to Flag
1. **God functions** - >100 lines, multiple responsibilities
2. **Code duplication** - Same logic across multiple files
3. **Weak types** - Any, dict, list without generics, missing type hints
4. **Magic strings/numbers** - Should be enums/constants
5. **Type-deficient patterns** - hasattr/getattr usage
6. **Dead code** - Commented code, unused functions
7. **Cross-file patterns** - Same validation repeated in multiple places

## What NOT to Flag
- Variable naming (unless truly confusing)
- Line length
- Comment style
- Whitespace
- Import order

## Output Format

### 🔴 EGREGIOUS ISSUES (Must Fix)

#### Issue #1: [Title]
**Files:** file.py:123, other.py:456
**Pattern:** [Describe the issue]
**Impact:** [Why this is bad]
**Fix:** [Specific actionable recommendation]

### 🟡 MODERATE ISSUES (Should Fix)
[Similar format]

### ✅ POSITIVE PATTERNS
[Good practices observed]

### 📊 Summary
- Egregious: X issues
- Moderate: Y issues
- Priority: [Top issue to fix first]

---

PROMPT_START

    echo "## Review Context"
    cat "$REVIEW_MODE"
    echo ""

    if [ -s "$DIFF_SRC" ]; then
        echo "## Production Code"
        echo '```diff'
        cat "$DIFF_SRC"
        echo '```'
        echo ""
    fi

    if [ -s "$DIFF_TESTS" ]; then
        echo "## Test Code"
        echo '```diff'
        cat "$DIFF_TESTS"
        echo '```'
    fi
}

echo "Starting LLM code review..."
echo "Model: ${MODEL_ARG:-default}"
echo ""

# Run the review
build_prompt | llm $MODEL_ARG

echo ""
echo "---"
echo "Review complete. Use findings as hints for deeper investigation."
