#!/bin/bash
# Extract changes for code review based on mode (PR branch, commit, or path)
#
# Usage:
#   ./extract-changes.sh              # PR: current branch vs main
#   ./extract-changes.sh abc123       # Commit: specific commit
#   ./extract-changes.sh auth/login   # Path: fuzzy match files
#
# Environment variables:
#   SRC_DIR     Source directory (default: src/)
#   TEST_DIR    Test directory (default: tests/)
#   OUTPUT_DIR  Output directory (default: /tmp)

set -e

ARG="$1"
SRC_DIR="${SRC_DIR:-src/}"
TEST_DIR="${TEST_DIR:-tests/}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"

# Output files
DIFF_SRC="$OUTPUT_DIR/diff-src.txt"
DIFF_TESTS="$OUTPUT_DIR/diff-tests.txt"
REVIEW_MODE="$OUTPUT_DIR/review-mode.txt"

# Lock file patterns to exclude
LOCK_EXCLUDES=(':!uv.lock' ':!poetry.lock' ':!package-lock.json' ':!yarn.lock' ':!*.lock')

calc_metadata() {
    local src_file="$1"
    local test_file="$2"
    local mode_file="$3"

    SRC_SIZE=$(wc -c < "$src_file" 2>/dev/null || echo "0")
    TEST_SIZE=$(wc -c < "$test_file" 2>/dev/null || echo "0")
    TOTAL_SIZE=$((SRC_SIZE + TEST_SIZE))
    TOTAL_SIZE_KB=$(echo "scale=2; $TOTAL_SIZE / 1024" | bc)
    SRC_LINES=$(wc -l < "$src_file" 2>/dev/null || echo "0")
    TEST_LINES=$(wc -l < "$test_file" 2>/dev/null || echo "0")
    SRC_FILES=$(grep -c '^diff --git\|^+++' "$src_file" 2>/dev/null || echo "0")
    TEST_FILES=$(grep -c '^diff --git\|^+++' "$test_file" 2>/dev/null || echo "0")

    echo "DIFF_SIZE_KB: $TOTAL_SIZE_KB" >> "$mode_file"
    echo "SRC_FILES: $SRC_FILES" >> "$mode_file"
    echo "TEST_FILES: $TEST_FILES" >> "$mode_file"
    echo "Production lines: $SRC_LINES" | tee -a "$mode_file"
    echo "Test lines: $TEST_LINES" | tee -a "$mode_file"
}

if [ -z "$ARG" ]; then
    # MODE: PR branch vs main
    BASE_BRANCH=$(git rev-parse --abbrev-ref main 2>/dev/null || git rev-parse --abbrev-ref master 2>/dev/null || echo "main")
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

    echo "=== PR Review: $CURRENT_BRANCH vs $BASE_BRANCH ===" > "$REVIEW_MODE"
    echo "MODE: pr" >> "$REVIEW_MODE"
    echo "CURRENT_BRANCH: $CURRENT_BRANCH" >> "$REVIEW_MODE"
    echo "BASE_BRANCH: $BASE_BRANCH" >> "$REVIEW_MODE"

    # Extract PR changes
    git diff "$BASE_BRANCH"...HEAD -- "$SRC_DIR" "${LOCK_EXCLUDES[@]}" > "$DIFF_SRC" 2>/dev/null || true
    git diff "$BASE_BRANCH"...HEAD -- "$TEST_DIR" "${LOCK_EXCLUDES[@]}" > "$DIFF_TESTS" 2>/dev/null || true

    calc_metadata "$DIFF_SRC" "$DIFF_TESTS" "$REVIEW_MODE"

elif git show "$ARG" --quiet 2>/dev/null; then
    # MODE: Specific commit
    echo "=== Commit Review: $ARG ===" > "$REVIEW_MODE"
    echo "MODE: commit" >> "$REVIEW_MODE"
    echo "COMMIT_HASH: $ARG" >> "$REVIEW_MODE"
    echo "COMMIT_TITLE: $(git log -1 --format=%s "$ARG")" >> "$REVIEW_MODE"
    echo "COMMIT_DATE: $(git log -1 --format=%ci "$ARG")" >> "$REVIEW_MODE"
    echo "COMMIT_AUTHOR: $(git log -1 --format=%an "$ARG")" >> "$REVIEW_MODE"

    # Extract commit changes
    git show "$ARG" -- "$SRC_DIR" "${LOCK_EXCLUDES[@]}" > "$DIFF_SRC" 2>/dev/null || true
    git show "$ARG" -- "$TEST_DIR" "${LOCK_EXCLUDES[@]}" > "$DIFF_TESTS" 2>/dev/null || true

    calc_metadata "$DIFF_SRC" "$DIFF_TESTS" "$REVIEW_MODE"

else
    # MODE: Path pattern (fuzzy match)
    echo "=== Path Review: $ARG ===" > "$REVIEW_MODE"
    echo "MODE: path" >> "$REVIEW_MODE"
    echo "PATTERN: $ARG" >> "$REVIEW_MODE"

    # Fuzzy path matching: convert slashes to .*, hyphens to [_-]
    SEARCH_PATTERN=$(echo "$ARG" | sed 's|/|.*|g' | sed 's|-|[_-]|g')
    echo "SEARCH_REGEX: $SEARCH_PATTERN" >> "$REVIEW_MODE"

    # Find matching files
    SRC_FILES=$(find "$SRC_DIR" -type f -name "*.py" 2>/dev/null | grep -iE "$SEARCH_PATTERN" | grep -v __pycache__ | head -50 || true)
    TEST_FILES_FOUND=$(find "$TEST_DIR" -type f -name "*.py" 2>/dev/null | grep -iE "$SEARCH_PATTERN" | grep -v __pycache__ | head -50 || true)

    ALL_FILES=$(echo -e "$SRC_FILES\n$TEST_FILES_FOUND" | sort -u | grep -v "^$" || true)

    if [ -z "$ALL_FILES" ]; then
        echo "ERROR: No files found matching '$ARG'" | tee "$DIFF_SRC" "$DIFF_TESTS"
        echo "Searched in: $SRC_DIR, $TEST_DIR"
        exit 1
    fi

    echo "=== MATCHED FILES ===" >> "$REVIEW_MODE"
    echo "$ALL_FILES" >> "$REVIEW_MODE"
    echo "Found $(echo "$ALL_FILES" | wc -l | tr -d ' ') files"

    # Clear output files
    > "$DIFF_SRC"
    > "$DIFF_TESTS"

    # Get current state of each file
    for file in $ALL_FILES; do
        echo "=== FILE: $file ===" >> "$REVIEW_MODE"

        # Check for uncommitted changes
        if git diff HEAD --quiet -- "$file" 2>/dev/null; then
            # No uncommitted changes, show file content
            CONTENT=$(git show HEAD:"$file" 2>/dev/null || cat "$file" 2>/dev/null || true)
        else
            # Show uncommitted changes as diff
            CONTENT=$(git diff HEAD -- "$file" 2>/dev/null || true)
        fi

        # Route to appropriate output file
        if echo "$file" | grep -q "^$TEST_DIR\|/tests/\|_test\.py$\|test_"; then
            echo "$CONTENT" >> "$DIFF_TESTS"
        else
            echo "$CONTENT" >> "$DIFF_SRC"
        fi
    done

    calc_metadata "$DIFF_SRC" "$DIFF_TESTS" "$REVIEW_MODE"
fi

echo ""
echo "Output files:"
echo "  Production: $DIFF_SRC ($(wc -l < "$DIFF_SRC" | tr -d ' ') lines)"
echo "  Tests:      $DIFF_TESTS ($(wc -l < "$DIFF_TESTS" | tr -d ' ') lines)"
echo "  Metadata:   $REVIEW_MODE"
echo ""
cat "$REVIEW_MODE"
