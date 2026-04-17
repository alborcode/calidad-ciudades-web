# What to Flag - Egregious Issues

## Focus on BIG Problems, Not Small Style Issues

### 1. Massive Code Duplication

**Same logic copy-pasted across files is the #1 problem.**

```python
# BAD - Same validation in two files
# file1.py
def process_user_data(user):
    if not user.get("email"):
        raise ValueError("Email required")
    if not user.get("name"):
        raise ValueError("Name required")
    return {"email": user["email"], "name": user["name"]}

# file2.py - DUPLICATE!
def validate_user(user):
    if not user.get("email"):
        raise ValueError("Email required")
    if not user.get("name"):
        raise ValueError("Name required")
    return {"email": user["email"], "name": user["name"]}

# GOOD - Extract once, reuse
# user_validation.py
def validate_user_fields(user: User) -> User:
    if not user.email:
        raise ValueError("Email required")
    if not user.name:
        raise ValueError("Name required")
    return user
```

### 2. Repeated Patterns (3+ instances = extract)

```python
# BAD - Pattern repeated 5 times across files
result = await api_client.get(url)
if result.status_code != 200:
    logger.error(f"API call failed: {result.status_code}")
    raise APIError(f"Failed: {result.status_code}")
data = result.json()

# GOOD - Extract pattern
async def fetch_api_data(url: str) -> dict:
    result = await api_client.get(url)
    if result.status_code != 200:
        logger.error(f"API call failed: {result.status_code}")
        raise APIError(f"Failed: {result.status_code}")
    return result.json()
```

### 3. Related Classes Without Shared Interface

**Classes with >50% method overlap should inherit from ABC to prevent drift.**

```python
# BAD - Related classes with drifting interfaces
class CacheDirectory:
    def list_entries(self, filter=None): ...
    def count(self, filter=None): ...
    def get(self, cache_key: str): ...

class StatusDirectory:
    def get_all_entries(self): ...  # Different name!
    def total_count(self): ...  # Different name!
    def find(self, run_id: str): ...  # Different name!

# GOOD - ABC enforces consistent interface
class FileDirectoryBase(ABC, Generic[T]):
    @abstractmethod
    def list_entries(self) -> list[T]: ...
    @abstractmethod
    def count(self) -> int: ...
    @abstractmethod
    def get(self, key: str) -> T | None: ...

class CacheDirectory(FileDirectoryBase[CacheEntry]):
    def list_entries(self, filter=None): ...  # Extra params OK
    def count(self, filter=None): ...
    def get(self, key: str): ...

class StatusDirectory(FileDirectoryBase[StatusEntry]):
    def list_entries(self): ...  # Must match interface
    def count(self): ...
    def get(self, key: str): ...  # Parameter name enforced
```

**When to use ABCs:**
- Two classes have >50% method overlap
- Classes will be used interchangeably
- Extracting patterns from duplicated code
- Method names/signatures must stay synchronized

### 4. Meaningless Tests

```python
# BAD - Tests that don't verify behavior
def test_user_created():
    user = User(name="Bob", email="bob@example.com")
    assert user is not None  # Meaningless - constructor always returns object
    assert user.name == "Bob"  # Just testing assignment

# GOOD - Tests that verify invariants
def test_user_email_must_be_valid():
    """INVARIANT: User email must contain @ symbol and domain."""
    with pytest.raises(ValidationError):
        User(name="Bob", email="invalid-email")

    with pytest.raises(ValidationError):
        User(name="Bob", email="bob@")
```

### 5. Dead Code

**Look for:**
- Functions never called (search codebase for usages)
- Commented-out code blocks
- Imports not used
- Parameters never accessed

```python
# BAD
def process_data(data, legacy_mode=False, debug=False):
    # legacy_mode and debug are never used anywhere
    return transform(data)

# GOOD
def process_data(data):
    return transform(data)
```

### 6. God Functions (100+ lines)

```python
# BAD - 200 line function doing everything
def process_order(order_data):
    # 50 lines of validation
    # 30 lines of transformation
    # 40 lines of API calls
    # 30 lines of database updates
    # 50 lines of error handling
    ...

# GOOD - Extract responsibilities
def process_order(order_data: OrderData) -> ProcessedOrder:
    validated = _validate_order(order_data)
    transformed = _transform_order(validated)
    api_result = _call_payment_api(transformed)
    return _save_order(transformed, api_result)
```

### 7. Weak Types - The Silent Killer

**ALWAYS flag these patterns:**

```python
# Any - Type checking disabled
def process_data(data: Any) -> Any:
    return data.get("value")

# object - Equally useless
def handle_response(response: object) -> dict:
    return response.json()  # Type checker can't verify this exists

# Raw dict/list/tuple without element types
def get_users() -> list:  # List of what?
    return [{"name": "Bob", "age": 30}]

def get_config() -> dict:  # Dict with what keys/values?
    return {"timeout": 30}

# Missing types entirely
def calculate(x, y):
    return x + y

# GOOD - Specific types
class User(BaseModel):
    name: str
    age: int

def get_users() -> list[User]:
    return [User(name="Bob", age=30)]

def get_config() -> AppConfig:
    return AppConfig(timeout=30)

def calculate(x: int, y: int) -> int:
    return x + y
```

### 8. hasattr/getattr - Markers of Type Deficiency

**hasattr and getattr indicate missing/incorrect types.**

```python
# BAD - Using hasattr because type is wrong
def process(obj: Any):
    if hasattr(obj, "name"):
        return obj.name
    return None

# GOOD - Use proper types/protocols
class Named(Protocol):
    name: str

def process(obj: Named) -> str:
    return obj.name  # Type checker verifies this exists

# BAD - getattr for dynamic access
def get_field(obj: dict, field_name: str) -> Any:
    return getattr(obj, field_name, None)

# GOOD - Use TypedDict or Pydantic
class UserData(BaseModel):
    name: str
    email: str
    age: int

def get_field(user: UserData, field_name: str) -> str | int:
    match field_name:
        case "name" | "email":
            return getattr(user, field_name)
        case "age":
            return user.age
```

**General Principle:** If using hasattr/getattr, ask: "Why don't I know the type?"

---

## What NOT to Flag

These are auto-fixable or minor - focus on structural problems:
- Variable naming (unless truly confusing)
- Line length (unless absurdly long)
- Comment style
- Whitespace
- Import order
