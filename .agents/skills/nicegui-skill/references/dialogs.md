# Dialogs & Notifications

Quick reference for dialogs, notifications, and alerts in NiceGUI.

## Notifications (Toast)

### ui.notify(message, position='bottom', type=None, ...)

Toast notification.

```python
# Basic
ui.notify('Hello!')

# Position
ui.notify('Top Right', position='top-right')
ui.notify('Center', position='center')

# Types
ui.notify('Success!', type='positive')
ui.notify('Error!', type='negative')
ui.notify('Warning!', type='warning')
ui.notify('Info', type='info')

# With close button
ui.notify('Dismiss me', close_button='Close')

# Multi-line
ui.notify('Line 1\nLine 2\nLine 3', multi_line=True)
```

### Notification Options

```python
ui.notify(
    message='Custom notification',
    position='bottom',
    type='positive',
    close_button=True,
    color=None,
    multi_line=False,
    timeout=5,
    actions=[
        {'text': 'View', handler': view_handler},
        {'text': 'Dismiss', handler': dismiss_handler}
    ]
)
```

## Dialogs

### ui.dialog()

Modal dialog (awaitable).

```python
with ui.dialog() as dialog, ui.card():
    ui.label('Are you sure?')
    with ui.row():
        ui.button('Yes', on_click=lambda: dialog.submit(True))
        ui.button('No', on_click=lambda: dialog.submit(False))

async def confirm():
    result = await dialog
    ui.notify(f'Result: {result}')

ui.button('Open', on_click=confirm)
```

### Dialog with Form

```python
with ui.dialog() as dialog, ui.card():
    name_input = ui.input(label='Name')
    email_input = ui.input(label='Email')
    with ui.row():
        ui.button('Cancel', on_click=lambda: dialog.submit(None))
        ui.button('Submit', on_click=lambda: dialog.submit({
            'name': name_input.value,
            'email': email_input.value
        }))

async def open_form():
    result = await dialog
    if result:
        ui.notify(f'Submitted: {result}')
```

### Dialog with Backdrop

```python
with ui.dialog().props('backdrop-filter="blur(8px)"') as d:
    ui.label('Press ESC to close')
    ui.button('Close', on_click=d.close)
```

## Alert Dialogs

### ui.alert(title='', message='', severity='info', ...)

Simple alert dialog.

```python
await ui.alert(title='Info', message='This is information')
await ui.alert(title='Success', message='Operation completed', severity='positive')
await ui.alert(title='Warning', message='Please check input', severity='warning')
await ui.alert(title='Error', message='Something failed', severity='negative')
```

### Confirm Dialog

```python
async def confirm_delete():
    confirmed = await ui.confirm(title='Confirm', message='Delete this item?')
    if confirmed:
        delete_item()
        ui.notify('Deleted!', type='positive')
```

### ui.confirm(title='', message='')

Confirmation dialog.

```python
confirmed = await ui.confirm(
    title='Delete',
    message='Are you sure you want to delete this item?'
)
```

## Prompt Dialogs

### ui.prompt(title='', message='', default='', validate=None)

Input prompt dialog.

```python
name = await ui.prompt(title='Enter Name', message='What is your name?')
if name:
    ui.notify(f'Hello, {name}!')
```

## Drawers (Side Panels)

### ui.drawer()

Side drawer (similar to dialog but from side).

```python
with ui.drawer().classes('bg-grey-2'):
    ui.label('Drawer content')

# Toggle
drawer = ui.drawer()
ui.button('Toggle', on_click=lambda: drawer.toggle())
```

### ui.left_drawer() / ui.right_drawer()

Side-specific drawers.

```python
with ui.left_drawer().classes('bg-blue-1'):
    ui.label('Navigation')

with ui.right_drawer():
    ui.label('Settings')
```

## Message Boxes

### Custom Message Box Pattern

```python
async def message_box(title, message, buttons):
    with ui.dialog() as dialog, ui.card():
        ui.label(title).classes('text-h6')
        ui.label(message)
        with ui.row():
            for text, value in buttons:
                ui.button(text, on_click=lambda v=value: dialog.submit(v))
    
    return await dialog

# Usage
result = await message_box(
    'Choose Option',
    'What would you like to do?',
    [('Option A', 'a'), ('Option B', 'b'), ('Cancel', None)]
)
```

## Event Handling

### Dialog Events

```python
dialog = ui.dialog()
dialog.on('show', lambda: ui.notify('Dialog opened'))
dialog.on('hide', lambda: ui.notify('Dialog closed'))
dialog.on('escape-key', lambda: ui.notify('ESC pressed'))
```

## Common Patterns

```python
# Chained notifications
ui.notify('Step 1 completed', type='positive')
ui.notify('Step 2 completed', type='positive')
ui.notify('All done!', type='positive')

# Loading state with dialog
with ui.dialog() as d, ui.card():
    ui.label('Processing...')
    ui.spinner(size='lg')

async def process():
    d.open()
    await do_work()
    d.close()
    ui.notify('Done!', type='positive')
```

## Props

```python
# Dialog positioning
ui.dialog().props('position=top')
ui.dialog().props('position=right')

# Fullscreen dialog
ui.dialog().props('fullscreen')

# Backdrop
ui.dialog().props('backdrop')
ui.dialog().props('no-backdrop')

# Close behavior
ui.dialog().props('seamless')  # No border
```