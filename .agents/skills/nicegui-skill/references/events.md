# Events & Reactivity

> **Relacionado**: Ver [async.md](./async.md) para operaciones HTTP y background tasks

Quick reference for event handling and reactivity in NiceGUI.

## Event Handlers

### element.on(event_name, handler)

Generic event listener.

```python
button = ui.button('Click')

# Basic handler
button.on('click', lambda: ui.notify('Clicked!'))

# With event arguments
button.on('click', lambda e: ui.notify(f'Button: {e.sender}'))

# With throttle
text_input.on('input', handler, throttle=0.5)

# With js_handler (client-side)
button.on('click', js_handler='() => alert("Hello!")')
```

### element.on_click(handler)

Click event shortcut.

```python
ui.button('Click me').on_click(lambda: ui.notify('Clicked!'))
```

### element.on_value_change(handler)

Value change event.

```python
input_field = ui.input()
input_field.on_value_change(lambda e: ui.notify(f'Value: {e.value}'))
```

## Event Arguments

### ClickEventArguments
```python
def handler(e: events.ClickEventArguments):
    e.sender      # Element that triggered event
    e.client       # Client info
```

### ValueChangeEventArguments
```python
def handler(e: events.ValueChangeEventArguments):
    e.value        # New value
    e.value_copy   # Deep copy of value
```

### UploadEventArguments
```python
def handler(e: events.UploadEventArguments):
    e.name         # Filename
    e.content_type # MIME type
    e.content      # File bytes
```

## Reactive Binding

### bind_text_from(obj, attr, ...)

One-way binding (source → element).

```python
label.bind_text_from(input, 'value')
label.bind_text_from(input, 'value', transform=lambda v: f'Value: {v}')
```

### bind_text(obj, attr)

Two-way binding.

```python
input.bind_value(state, 'field')
```

### bind_visibility_from(obj, attr)

Reactive visibility.

```python
element.bind_visibility_from(toggle, 'value')
```

### bind_enabled_from(obj, attr)

Reactive enabled state.

```python
button.bind_enabled_from(input, 'value')
```

### bind_value(obj, attr)

Two-way value binding.

```python
input.bind_value(app_state, 'name')
```

## Refreshable Components

### @ui.refreshable

Decorator for refreshable UI components.

```python
@ui.refreshable
def counter():
    count, set_count = ui.state(0)
    ui.label(f'Count: {count}')
    ui.button('+1', on_click=lambda: set_count(count + 1))

# Initial render
counter()

# Refresh (re-renders the component)
counter.refresh()

# Refresh with new arguments
counter.refresh(new_arg)
```

### ui.state(initial)

Reactive state within refreshable components.

```python
value, set_value = ui.state('default')

# With complex state
data, set_data = ui.state({'key': 'value'})
```

### Global Scope Refreshable

```python
from datetime import datetime

@ui.refreshable
def clock():
    ui.label(datetime.now().strftime('%H:%M:%S'))

ui.button('Refresh', on_click=clock.refresh)
```

### Async Refreshable

```python
@ui.refreshable
async def async_component():
    await asyncio.sleep(1)
    ui.label('Updated!')

async def handle_click(e):
    e.sender.disable()
    await async_component.refresh()
    e.sender.enable()
```

## Client-Side Execution

### js_handler Parameter

Execute JavaScript on client.

```python
# Simple JS
ui.button('Copy').on('click', js_handler='''
    () => navigator.clipboard.writeText("Hello!")
''')

# With event data
ui.input().on('input', js_handler='''
    (e) => console.log(e.target.value)
''')
```

### ui.run_javascript(code)

Execute JavaScript from server.

```python
await ui.run_javascript('alert("Hello!")')
await ui.run_javascript('console.log("test")')
```

### Client Methods

```python
# Run method on client
result = await element.run_method('focus')
result = await element.run_method('select')
```

## Throttling & Debouncing

### throttle Parameter

Minimum time between events.

```python
input.on('input', handler, throttle=0.5)  # Max 2 events/sec
```

### leading_events / trailing_events

Control event timing.

```python
# Trigger immediately on first event
input.on('input', handler, leading_events=True, trailing_events=False)

# Trigger after last event
input.on('input', handler, leading_events=False, trailing_events=True)
```

## Custom Events

### Emit Custom Event

```python
button.on('click', js_handler='''
    (e) => emit('my-event', {data: 'value'})
''')

# Listen for custom event
ui.label().on('my-event', handler)
```

## Common Patterns

```python
# Reactive label
name_input = ui.input(label='Name')
name_label = ui.label()
name_label.bind_text_from(name_input, 'value')

# Reactive visibility
with ui.row():
    toggle = ui.checkbox('Show')
    content = ui.label('Content here')
    content.bind_visibility_from(toggle, 'value')

# Conditional enabled
button = ui.button('Submit')
button.bind_enabled_from(input, 'value', lambda v: len(v) > 0)
```