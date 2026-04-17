# Code Bloat Patterns - What to Flag

**Why AI generates bloat:** AI finds it easier to write code on-the-spot than to search for existing patterns, recognize similarities, and reuse.

---

## Basic Bloat Patterns

### Repeated Function Calls in Expressions

```python
# BAD - load_filter_preset(name) called 6 times!
FilterPresetSummary(
    name=name,
    models=(load_filter_preset(name) or Filter()).models,
    levels=(load_filter_preset(name) or Filter()).levels,
    ids=(load_filter_preset(name) or Filter()).ids,
    versions=(load_filter_preset(name) or Filter()).versions,
    has_date_filter=(load_filter_preset(name) or Filter()).since is not None,
)

# GOOD - Load once, reuse
preset = load_filter_preset(name) or Filter()
FilterPresetSummary(
    name=name,
    models=preset.models,
    levels=preset.levels,
    ids=preset.ids,
    versions=preset.versions,
    has_date_filter=preset.since is not None,
)
```

### Duplicate Model Classes

```python
# BAD - Same class defined multiple times
# cache_models.py
class CacheError(BaseModel):
    error: str
    suggestions: list[str]

# explore_models.py - DUPLICATE!
class ExploreError(BaseModel):
    error: str
    suggestions: list[str]

# GOOD - Define once, import/alias
# common.py
class CommandError(BaseModel):
    error: str
    suggestions: list[str]

# cache_models.py
from common import CommandError as CacheError
```

### Field-by-Field Copies Instead of Inheritance

```python
# BAD - Duplicating parent fields
class CacheFilter(BaseModel):
    models: list[str]
    levels: list[str]
    ids: list[str]
    # ... 8 more fields

class FilterShowResult(BaseModel):  # DUPLICATES all CacheFilter fields!
    name: str
    models: list[str]        # duplicate
    levels: list[str]        # duplicate
    ids: list[str]           # duplicate

# GOOD - Use inheritance
class FilterShowResult(CacheFilter):
    """Extends CacheFilter with a name field."""
    name: str  # Only the new field
```

### Field-by-Field Construction Instead of Spread

```python
# BAD - Manual field copying
result = FilterShowResult(
    name=name,
    models=preset.models,
    levels=preset.levels,
    ids=preset.ids,
    versions=preset.versions,
    # ... 5 more fields
)

# GOOD - Use model_dump() spread
result = FilterShowResult(name=name, **preset.model_dump())

# BAD - Copying to create modified version
filtered_stats = StatsResult(
    task=stats.task,
    versions=[v for v in stats.versions if v.version == version],
    total_runs=stats.total_runs,
    # ... more fields
)

# GOOD - Use model_copy() with update
filtered_stats = stats.model_copy(
    update={"versions": [v for v in stats.versions if v.version == version]}
)
```

### Duplicate Logic Across Files

```python
# BAD - Same discovery logic in multiple places
# task_discovery.py
def _discover_task_names_local(self) -> list[str]:
    return [d.name for d in self.evaluations_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")]

# config.py - DUPLICATED!
def discover_task_names() -> list[str]:
    return [d.name for d in evaluations_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")]

# GOOD - Single source of truth
# config.py - canonical implementation
def discover_task_names(evaluations_dir: Path | None = None) -> list[str]:
    dir = evaluations_dir or default_evaluations_dir
    return [d.name for d in dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")]

# task_discovery.py - delegates
def _discover_task_names_local(self) -> list[str]:
    return Config.discover_task_names(self.evaluations_dir)
```

### Repeated CLI Option Definitions

```python
# BAD - Same Typer options in each file
# run.py
def run_command(
    task: Annotated[str, typer.Argument(help="Task name")],
    schema: Annotated[str, typer.Option("--schema", "-s", help="Schema version")],
    inputs: Annotated[list[str] | None, typer.Option("--inputs", "-i", help="Input IDs")],
):

# judge.py - SAME OPTIONS!
def judge_command(
    task: Annotated[str, typer.Argument(help="Task name")],
    schema: Annotated[str, typer.Option("--schema", "-s", help="Schema version")],
    inputs: Annotated[list[str] | None, typer.Option("--inputs", "-i", help="Input IDs")],
):

# GOOD - Define once in common.py
TaskArg = Annotated[str, typer.Argument(help="Task name")]
SchemaOpt = Annotated[str, typer.Option("--schema", "-s", help="Schema version")]
InputsOpt = Annotated[list[str] | None, typer.Option("--inputs", "-i", help="Input IDs")]

# run.py
def run_command(task: TaskArg, schema: SchemaOpt, inputs: InputsOpt):

# judge.py
def judge_command(task: TaskArg, schema: SchemaOpt, inputs: InputsOpt):
```

### Repeated Test Patterns

```python
# BAD - Same test structure copy-pasted
class TestProgressInfoDefaults:
    def test_default_completed(self):
        info = ProgressInfo()
        assert info.completed == 0

class TestCurrentItemDefaults:  # SAME PATTERN!
    def test_default_item(self):
        info = CurrentItem()
        assert info.item is None

# GOOD - Parameterize
@pytest.mark.parametrize("model_class,field,default_value", [
    (ProgressInfo, "completed", 0),
    (CurrentItem, "item", None),
    (TimingInfo, "elapsed_seconds", 0.0),
])
def test_model_defaults(model_class, field, default_value):
    instance = model_class()
    assert getattr(instance, field) == default_value
```

---

## Advanced Bloat Patterns

### God Function Decomposition

```python
# BAD - Monolithic function
async def _run_benchmark_async(task, version, ...):  # 315 lines!
    # 50 lines: load inputs
    # 40 lines: create benchmark record
    # 80 lines: build tasks
    # 100 lines: process results
    # 45 lines: save and report

# GOOD - Orchestrator with focused helpers
async def _run_benchmark_async(task, version, ...):
    inputs = _load_benchmark_inputs(task, discovery)
    record = _create_benchmark_record(task, version, config)
    tasks = _build_benchmark_tasks(inputs, config, record)
    results = await executor.execute(tasks)
    return _process_benchmark_results(results, record)
```

### Multiple Services -> Single Consolidated Service

```python
# BAD - Related functionality split
# StatusService - fetches execution status
# TestService - executes tests
# OrchestrationService - partial orchestration

# GOOD - Single service with cohesive responsibility
class OrchestrationService:
    """Orchestrates all operations."""
    async def execute(self, ...) -> ExecutionResult: ...
    async def get_status(self, ...) -> list[ExecutionStatus]: ...
    async def run_test(self, ...) -> TestResult: ...
```

**Warning signs:**
- Multiple services with overlapping method names
- UI creating multiple service instances for one workflow
- Same model types returned by different services

### Same Fix Across Multiple Files -> Shared Utility

```python
# BAD - Same fix copy-pasted
# service_a.py
try:
    results = await asyncio.gather(*tasks, return_exceptions=True)
except Exception as e:
    logger.error(...)

# service_b.py - SAME PATTERN

# GOOD - Extract utility after seeing pattern twice
async def safe_gather(*coros, fail_fast: bool = True) -> list[Any]:
    """Gather with fail-fast behavior and proper error handling."""
    ...
```

**Rule of thumb:** Same change in 3+ files -> stop and create utility. Already in 2 files -> go back and consolidate.

---

## Extended Code Review Checklist

Scan for AI-generated bloat:

- [ ] **God functions** - Any function >100 lines?
- [ ] **Hardcoded values** - Magic strings that should be enums or discovered?
- [ ] **Service sprawl** - Multiple services doing related things?
- [ ] **Repeated fixes** - Same change in multiple files?
- [ ] **String-encoded data** - Structured data hiding in strings?
- [ ] **Missed reuse** - New class that duplicates existing one?
- [ ] **Copy-paste helpers** - Same test helper in multiple files?
- [ ] **Public method duplication** - Two methods with 80%+ identical logic?
- [ ] **Test mock setup duplication** - Same mock setup in 3+ tests?
- [ ] **Context manager pairs** - Two context managers always used together?
- [ ] **Naming inconsistency** - Different conventions in config/model names?
- [ ] **Registry class drift** - 3+ registry classes with different method names?

**General principle:** AI generates code faster than it searches. Counteract by actively looking for reuse opportunities.
