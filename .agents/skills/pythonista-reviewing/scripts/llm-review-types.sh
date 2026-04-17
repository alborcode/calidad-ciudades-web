#!/bin/bash
# Run LLM-based TYPE HINT review on extracted source changes
#
# Prerequisites:
#   - Simon Willison's llm tool: pip install llm
#
# Usage:
#   ./llm-review-types.sh                    # Review with default model
#   ./llm-review-types.sh -m gpt-4o          # Use specific model

set -e

OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
DIFF_SRC="$OUTPUT_DIR/diff-src.txt"
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

if [ ! -s "$DIFF_SRC" ]; then
    echo "No source changes to review for types."
    echo "Run extract-changes.sh first."
    exit 0
fi

# Build the type review prompt
build_prompt() {
    cat << 'PROMPT_START'
# Type Hint Review Instructions

Review this code for TYPE HINT issues ONLY. Find:

1. **Bare containers** - `dict`, `list`, `tuple` without element types
   - Bad: `def get_data() -> dict:`
   - Good: `def get_data() -> dict[str, UserData]:`

2. **Missing return types** - Functions without return type hints
   - Bad: `def process(x):`
   - Good: `def process(x: Input) -> Output:`

3. **Weak Any patterns** - `Dict[str, Any]` that should be Pydantic models
   - Bad: `config: Dict[str, Any]`
   - Good: `config: AppConfig`

4. **Complex nested types** - Deep nesting that needs named types
   - Bad: `Dict[str, List[Tuple[int, str, Optional[float]]]]`
   - Good: `Dict[str, List[DataPoint]]` with `DataPoint` as Pydantic model

5. **hasattr/getattr patterns** - Indicate missing type information
   - Bad: `if hasattr(obj, "name"): return obj.name`
   - Good: Use Protocol or proper type annotation

## Output Format

For each issue found:
```
file.py:123 - Current: `def foo() -> dict:` → Fix: `def foo() -> dict[str, Item]:`
```

Group by severity:
- 🔴 CRITICAL: Missing types on public APIs
- 🟡 MODERATE: Internal functions, complex types
- ℹ️ INFO: Suggestions for better types

---

PROMPT_START

    echo "## Review Context"
    cat "$REVIEW_MODE" 2>/dev/null || echo "No context available"
    echo ""

    echo "## Code to Review for Type Hints"
    echo '```diff'
    cat "$DIFF_SRC"
    echo '```'
}

echo "Starting LLM type hint review..."
echo "Model: ${MODEL_ARG:-default}"
echo ""

build_prompt | llm $MODEL_ARG

echo ""
echo "---"
echo "Type review complete."
