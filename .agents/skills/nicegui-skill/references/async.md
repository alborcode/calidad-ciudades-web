# Async & Background Tasks

> **Relacionado**: Ver [events.md](./events.md) para event handlers y binding

Quick reference for asynchronous programming, background tasks, and API communication in NiceGUI.

## Async Basics

### Async Page Functions

```python
@ui.page('/async')
async def async_page():
    ui.label('Loading...')
    await asyncio.sleep(1)  # Non-blocking wait
    ui.label('Done!')
```

### Await Client Connection

```python
@ui.page('/wait')
async def wait_page():
    ui.label('Immediate content')
    await ui.context.client.connected()  # Wait for WebSocket
    ui.label('Client connected!')
```

## Background Tasks

### background_tasks.create()

Run async function in background.

```python
import asyncio
from nicegui import background_tasks, ui

async def long_task():
    await asyncio.sleep(5)
    ui.notify('Task completed!')

ui.button('Start', on_click=lambda: background_tasks.create(long_task()))
```

### background_tasks.create_lazy()

Prevent duplicate tasks with same name.

```python
async def search(query):
    await asyncio.sleep(2)
    results = await api_search(query)
    display_results(results)

# Won't start new search if one is running
ui.input().on_value_change(
    lambda e: background_tasks.create_lazy(search(e.value), 'search')
)
```

### @background_tasks.await_on_shutdown

Ensure task completes on shutdown.

```python
@background_tasks.await_on_shutdown
async def backup_data():
    await save_to_disk()
    print('Backup complete')

# This will run even when server stops
```

## Global App Timer

### app.timer

UI-independent timer for background tasks.

```python
import asyncio
from nicegui import app, ui

counter = {'value': 0}

# Global timer - runs independently of UI
@app.timer(interval=1.0)  # Every 1 second
def timer_callback():
    counter['value'] += 1
    print(f'Counter: {counter["value"]}')

# To stop the timer
timer_callback.cancel()
```

### Timer Management

```python
# Store timer reference
timer = app.timer(5.0, my_callback)
timer.cancel()  # Stop timer
timer.restart()  # Restart
```

## HTTP Requests

### Using httpx (Async)

```python
import httpx
import asyncio

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com/data')
        return response.json()

# In async function
data = await fetch_data()
ui.label(str(data))
```

### With Loading State

```python
async def get_quote():
    btn.disable()
    btn.props('loading')
    
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.quotable.io/random')
        quote = response.json()['content']
    
    label.text = f'"{quote}"'
    btn.enable()
    btn.props(remove='loading')

btn = ui.button('Get Quote', on_click=get_quote)
```

### Concurrent Requests

```python
async def fetch_multiple():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get('https://api1.com'),
            client.get('https://api2.com'),
            client.get('https://api3.com'),
            return_exceptions=True
        )
    return results
```

## Search with Cancellation

### Cancel Previous Query

```python
running_query = None

async def search(e):
    global running_query
    
    # Cancel previous query if typing fast
    if running_query:
        running_query.cancel()
    
    # Start new search
    running_query = asyncio.create_task(
        api.get(f'https://api.com/search?q={e.value}')
    )
    results = await running_query
    display(results)

ui.input().on_value_change(search)
```

## Server Events (SSE)

### Server-Sent Events

```python
from fastapi import FastAPI
from fastapi.schemas import EventSourceResponse
import nicegui

app = FastAPI()

@app.get('/stream')
async def stream():
    '''Simple SSE endpoint'''
    async def generate():
        for i in range(10):
            yield {'event': 'message', 'data': f'count: {i}'}
            await asyncio.sleep(1)
    
    return EventSourceResponse(generate())

# Consume in NiceGUI
ui.label().on('message', handler)  # Via websocket event
```

## WebSocket Communication

### Direct WebSocket Access

```python
@ui.page('/ws_test')
async def ws_test():
    ws = ui.context.client.ws
    await ws.send({'type': 'ping'})
    
    async for message in ws:
        handle_message(message)
```

### Broadcast to All Clients

```python
from nicegui import app, ui

# Store connected clients
clients = set()

@ui.page('/broadcast_page')
def broadcast_page():
    clients.add(ui.context.client)
    # Remove on disconnect - use cleanup

async def notify_all(message):
    for client in clients:
        await client.send(message)
```

## Client-Side JavaScript Async

### Async JavaScript Execution

```python
# Fetch from client
result = await ui.run_javascript('''
    await fetch('/api/data').then(r => r.json())
''')
```

### Promise Resolution

```python
ui.button('Async JS').on('click', js_handler='''
    async () => {
        const data = await compute();
        emit('result', data);
    }
''')
```

## Common Patterns

```python
# Progress indicator during async operation
with ui.card():
    progress = ui.linear_progress(value=0)
    
    async def long_operation():
        for i in range(10):
            await asyncio.sleep(0.5)
            progress.set_value((i + 1) * 10)
        ui.notify('Complete!')
    
    ui.button('Start', on_click=lambda: background_tasks.create(long_operation()))

# Debounced search
debounce_timer = None

async def debounced_search(text):
    global debounce_timer
    if debounce_timer:
        debounce_timer.cancel()
    
    debounce_timer = asyncio.create_task(
        asyncio.sleep(0.5)  # Wait 500ms
    )
    await debounce_timer
    await actual_search(text)
```

## Error Handling

```python
async def safe_request():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
    except httpx.TimeoutException:
        ui.notify('Request timed out', type='warning')
    except Exception as e:
        ui.notify(f'Error: {e}', type='negative')
    return None
```