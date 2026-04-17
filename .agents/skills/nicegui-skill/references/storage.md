# App Storage & State

> **Relacionado**: Ver [events.md](./events.md) para ui.state y @ui.refreshable

Quick reference for application storage, state management, and cookies in NiceGUI.

## Storage Overview

### Available Storage Types

```python
# Browser storage (client-side, cookie-based)
app.storage.browser  # Shared across tabs, limited size

# User storage (server-side, persistent)
app.storage.user    # Per-user, shared across tabs

# Application storage (global, in-memory)
app.storage.general  # Global state, not user-specific
```

## Browser Storage

### app.storage.browser

Data stored in browser session cookie.

```python
from nicegui import app, ui

# Read
value = app.storage.browser.get('key')
value = app.storage.browser['key']  # Raises if not found

# Write
app.storage.browser['key'] = 'value'
app.storage.browser.update({'key1': 'val1', 'key2': 'val2'})

# Delete
del app.storage.browser['key']
app.storage.browser.pop('key', None)
```

### Unique Browser ID

```python
browser_id = app.storage.browser['id']  # Unique per browser session

# Track unique visitors
from collections import Counter
unique_visitors = Counter()

@ui.page('/')
def index():
    unique_visitors[app.storage.browser['id']] += 1
    ui.label(f'Unique visitors: {len(unique_visitors)}')
```

### Storage Secret (Required)

```python
ui.run(storage_secret='your-secret-key')
# Required for browser and user storage
```

## User Storage

### app.storage.user

Server-side per-user storage.

```python
# Read
user_data = app.storage.user.get('preferences')
user_data = app.storage.user.get('theme', 'light')  # Default

# Write
app.storage.user['theme'] = 'dark'
app.storage.user.update({
    'language': 'en',
    'notifications': True
})
```

### Use Case: User Preferences

```python
@ui.page('/settings')
def settings():
    # Load preferences
    theme = app.storage.user.get('theme', 'light')
    
    # Save preference
    ui.toggle(['Light', 'Dark'], value=theme).on_value_change(
        lambda e: set_app_storage('theme', e.value)
    )

def set_app_storage(key, value):
    app.storage.user[key] = value
```

## Application Storage

### app.storage.general

Global in-memory storage (shared across all users).

```python
# Initialize if not exists
if 'config' not in app.storage.general:
    app.storage.general['config'] = {}

# Access
app.storage.general['config']['max_users'] = 100
app.storage.general['last_update'] = datetime.now()
```

## Session Management

### Session ID

```python
session_id = app.storage.browser['id']  # Browser session
session_id = app.storage.user['id']    # User session (if logged in)
```

### Session Middleware

```python
ui.run(
    session_middleware_kwargs={
        'secret_key': 'secret',
        'session_cookie': 'nicegui-session',
        'max_age': 86400  # 24 hours in seconds
    }
)
```

### Clear Session

```python
def logout():
    # Clear user storage
    app.storage.user.clear()
    # Redirect to login
    ui.navigate.to('/login')
```

## Cookies

### Direct Cookie Access

```python
from nicegui import app, ui

# Set cookie (via response)
@ui.page('/set_cookie')
def set_cookie():
    # Use JavaScript for client-side cookies
    ui.run_javascript('document.cookie = "name=value; path=/"')

# Read cookies (client-side)
async def read_cookies():
    return await ui.run_javascript('document.cookie')
```

## State Patterns

### Global State

```python
app_state = {'count': 0}

@ui.page('/counter')
def counter_page():
    ui.label().bind_text_from(
        app_state, 'count', 
        lambda x: f'Count: {x}'
    )
    ui.button('+1', on_click=lambda: increment())

def increment():
    app_state['count'] += 1
```

### Per-User State

```python
# Using user storage
@ui.page('/todos')
def todos_page():
    todos = app.storage.user.setdefault('todos', [])
    
    for todo in todos:
        ui.checkbox(todo['text'], value=todo['done'])
    
    ui.button('Add', on_click=add_todo)
```

### Shared State Across Pages

```python
# In main.py
from nicegui import app, ui

app.storage.general['data'] = []

@ui.page('/')
def page1():
    app.storage.general['data'].append('from page1')

@ui.page('/page2')
def page2():
    ui.label(str(app.storage.general['data']))
```

## Persistence

### Auto-Save to Disk

```python
import json
import os

STORAGE_FILE = 'storage.json'

def save_storage():
    with open(STORAGE_FILE, 'w') as f:
        json.dump({
            'user': dict(app.storage.user),
            'general': dict(app.storage.general)
        }, f)

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
            app.storage.user.update(data.get('user', {}))
            app.storage.general.update(data.get('general', {}))

# Load on startup
load_storage()

# Auto-save on changes
ui.button('Save', on_click=save_storage)
```

## Common Patterns

```python
# Theme persistence
@ui.page('/')
def main():
    theme = app.storage.user.get('theme', 'light')
    if theme == 'dark':
        ui.dark().enable()
    
    ui.toggle(['Light', 'Dark'], value=theme).on_value_change(
        lambda e: save_theme(e.value)
    )

def save_theme(theme):
    app.storage.user['theme'] = theme
    ui.dark().set(theme == 'dark')

# Shopping cart
cart = app.storage.user.setdefault('cart', [])
add_to_cart = lambda item: cart.append(item)

# Language preference
app.storage.user.setdefault('language', 'en')
```

## Storage Limits

```python
# Browser storage: ~4KB total
# User storage: Server-side, virtually unlimited
# General storage: Server memory, use carefully
```