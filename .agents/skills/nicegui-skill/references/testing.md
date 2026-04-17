# Testing

Quick reference for testing NiceGUI applications.

## Testing Overview

NiceGUI provides built-in testing utilities for UI testing.

```python
# Install testing dependencies
pip install nicegui[testing]
# or
pip install pytest-playwright
```

## User Fixture (Recommended)

### Basic Test with User Fixture

```python
from nicegui import ui
from nicegui.testing import User
import pytest

async def test_click(user: User) -> None:
    await user.open('/')
    await user.should_see('Click me')
    user.find(ui.button).click()
    await user.should_see('Hello World!')
```

### Finding Elements

```python
# Find by element type
user.find(ui.button)
user.find(ui.input)
user.find(ui.label)

# Find by text
user.find('Submit')  # Finds element containing text
user.find('Username')

# Find by placeholder
user.find(ui.input, placeholder='Enter name')
```

### Interactions

```python
# Click
user.find('Button').click()

# Type
user.find(ui.input).type('text')
user.find('Username').type('user1')

# Trigger events
user.find(ui.input).trigger('keydown.enter')

# Select options
user.find(ui.select).select('Option')
```

### Assertions

```python
# Should see text
await user.should_see('Expected text')

# Should NOT see text
await user.should_not_see('Hidden text')

# Should see element
await user.should_see(ui.button)

# Should contain in page
await user.should_contain('Partial match')
```

## Screen Fixture (Selenium)

### Setup

```python
from nicegui.testing import screen
import pytest

def test_with_screen():
    screen.open('/')
    screen.should_contain('Welcome')
```

### Interactions

```python
screen.click('Button')
screen.type('text')
screen.type('Enter')  # Special keys
screen.select('Option')
```

### Locators

```python
screen.click('text=Button')  # By text
screen.click('css=#id')       # By CSS
screen.click('xpath=//button')  # By XPath
```

## user_simulation Context

### Low-Level Testing

```python
from nicegui.testing import user_simulation
from nicegui import ui

async def test_click_via_root():
    def root():
        ui.button('Click me', on_click=lambda: ui.notify('Hello World!'))

    async with user_simulation(root) as user:
        await user.open('/')
        await user.should_see('Click me')
        user.find(ui.button).click()
        await user.should_see('Hello World!')
```

### Test Main File

```python
async def test_via_main_file():
    async with user_simulation(main_file='app.py') as user:
        await user.open('/')
        await user.should_see('Main file content')
```

## Multi-User Testing

### Parallel User Simulation

```python
from nicegui.testing import User
from nicegui import ui

async def test_chat(create_user):
    # Create multiple users
    user1 = create_user()
    await user1.open('/')
    
    user2 = create_user()
    await user2.open('/')

    # User 1 sends message
    user1.find(ui.input).type('Hello').trigger('keydown.enter')
    
    # User 2 sees it
    await user2.should_see('Hello')
```

## Async Testing

### pytest-asyncio

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async():
    await async_operation()
```

### Fixture

```python
@pytest.fixture
async def user():
    async with user_simulation(main_file='app.py') as u:
        yield u
```

## Test Structure

### Standard pytest Setup

```python
# conftest.py
import pytest
from nicegui.testing import User

@pytest.fixture
def create_user():
    async def _create_user():
        return User(main_file='app.py')
    return _create_user

# test_app.py
async def test_app(create_user):
    user = await create_user()
    await user.open('/')
    await user.should_see('Welcome')
```

### Example: Full Test

```python
# app.py
from nicegui import ui

@ui.page('/')
def index():
    username = ui.input(label='Username')
    password = ui.input(label='Password', password=True)
    ui.button('Log in', on_click=lambda: ui.notify(f'Welcome {username.value}'))

# test_app.py
import pytest
from nicegui import ui
from nicegui.testing import User

@pytest.fixture
def app():
    from app import index
    return index

@pytest.mark.asyncio
async def test_login():
    async with user_simulation(main_file='app.py') as user:
        await user.open('/')
        
        user.find(ui.input, label='Username').type('admin')
        user.find(ui.input, label='Password').type('secret').trigger('keydown.enter')
        
        await user.should_see('Welcome admin')
```

## Screen Testing (Selenium)

### Basic Usage

```python
from nicegui.testing import screen
from selenium.webdriver.common.keys import Keys

def test_login():
    screen.open('/')
    screen.type('Username')  # Types into first input
    screen.type(Keys.TAB)
    screen.type('password')
    screen.click('Log in')
    screen.should_contain('Welcome')
```

### Wait Conditions

```python
screen.should_contain('Text')  # Default timeout 5s
screen.should_not_contain('Hidden')

# Explicit wait
screen.wait_for('Element to appear')
```

## Best Practices

```python
# 1. Use User fixture for fast tests
async def test_ui(user: User):
    await user.open('/')
    # ... assertions

# 2. Test one thing per test
async def test_button_click(user: User):
    await user.open('/')
    user.find(ui.button).click()
    await user.should_see('Clicked!')

# 3. Use clear test names
async def test_login_with_valid_credentials(user: User):
    ...

# 4. Clean up resources
async def test_cleanup(user: User):
    try:
        await user.open('/')
    finally:
        # Cleanup if needed
        pass

# 5. Use trigger for keyboard events
user.find(ui.input).trigger('keydown.enter')
user.find(ui.input).trigger('blur')
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .[testing]
      - run: npx playwright install --with-deps
      - run: pytest
```

### Run Tests

```bash
pytest                    # Run all tests
pytest tests/             # Specific directory
pytest -v                # Verbose
pytest -k "test_name"    # By pattern
```