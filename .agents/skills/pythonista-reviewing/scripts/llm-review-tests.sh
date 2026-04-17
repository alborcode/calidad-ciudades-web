#!/bin/bash
# Run LLM-based TEST QUALITY review on extracted test changes
#
# Prerequisites:
#   - Simon Willison's llm tool: pip install llm
#   - A configured model: llm keys set openai / llm install llm-claude-3
#
# Usage:
#   ./llm-review-tests.sh                    # Review with default model
#   ./llm-review-tests.sh -m gpt-4o          # Use specific model

set -e

OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
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
    echo "Install with: pip install llm"
    exit 1
fi

if [ ! -s "$DIFF_TESTS" ]; then
    echo "No test changes to review."
    echo "Run extract-changes.sh first."
    exit 0
fi

# Build the test review prompt
build_prompt() {
    cat << 'PROMPT_START'
# Test Quality Review Instructions

You are reviewing TEST CODE for quality issues. Be critical, not confirmatory.

## Testing Rules to Enforce

**Critical Rules:**
- Never mock Pydantic models or data classes
- Always use `patch.object` instead of `patch` with string paths
- Create test data using Pydantic models, NOT naked dicts/JSON
- Write INVARIANT-based tests (what should always be true)
- NEVER write bug-affirming tests (merely proving a bug existed)
- Assert on BEHAVIOR/OUTCOMES, not implementation details
- Access mock calls with `.args[N]` / `.kwargs["name"]`, not `call[0][0]`

## Test Anti-Patterns to Flag

1. **Bug-affirming tests** - Tests that prove a bug existed vs testing invariants
2. **Mocking the SUT** - Mocking the System Under Test itself
3. **Implementation detail testing** - Asserting HOW instead of WHAT
4. **Meaningless tests** - Tests that don't verify anything useful
5. **Weak test data** - Naked dicts instead of Pydantic models
6. **Cryptic mock indexing** - Using `call[1][0]` instead of `.args/.kwargs`
7. **Manual state setup** - Setting up what production code should create
8. **Missing edge cases** - Happy path only, no error scenarios

## Output Format

### 🔴 EGREGIOUS TEST ISSUES

#### Issue #1: [Title]
**Files:** test_file.py:123
**Pattern:** [What's wrong - be specific]
**Impact:** [Why this test doesn't provide value]
**Fix:** [How to make it test invariants/behavior]

### 🟡 MODERATE TEST ISSUES
[Similar format]

### ✅ POSITIVE TEST PATTERNS
[Good practices observed]

### 📊 Summary
- Test Quality Score: X/10
- Priority: [Top issue to fix first]

---

PROMPT_START

    echo "## Review Context"
    cat "$REVIEW_MODE" 2>/dev/null || echo "No context available"
    echo ""

    echo "## Test Code to Review"
    echo '```diff'
    cat "$DIFF_TESTS"
    echo '```'
}

echo "Starting LLM test review..."
echo "Model: ${MODEL_ARG:-default}"
echo ""

build_prompt | llm $MODEL_ARG

echo ""
echo "---"
echo "Test review complete."
