# Input Controls

> **Relacionado**: Ver [events.md](./events.md) para manejo de eventos de cambio de valor

Quick reference for all input elements in NiceGUI.

## Text Inputs

### ui.input(label='', placeholder='', value='')

Single-line text input.

```python
name = ui.input(label='Name', placeholder='Enter your name')
email = ui.input(label='Email', value='user@example.com')

# Validation
ui.input(label='Email', validation={'Invalid email': lambda v: '@' in v})

# With prefix/suffix
ui.input(label='URL', placeholder='https://').props('prefix')
ui.input(label='Price', value='100').props('suffix="$"')

# Password with toggle
password = ui.input(label='Password', password=True, password_toggle_button=True)
```

### ui.textarea(label='', placeholder='')

Multi-line text input.

```python
bio = ui.textarea(label='Bio', placeholder='Tell us about yourself')
bio.bind_value(app_state, 'bio')  # Bind to state

# With character counter
ui.textarea(label='Message').props('counter maxlength=200')
```

## Numeric Inputs

### ui.number(label='', value=None, min=None, max=None, step=None)

Numeric input with increment/decrement.

```python
price = ui.number(label='Price', value=0, min=0, max=1000, step=0.01)
age = ui.number(label='Age', value=18, min=0, max=150, step=1)

# With prefix/suffix
quantity = ui.number(label='Qty', value=1, step=1).props('prefix')
ui.number(label='Amount', value=100).props('suffix="USD"')
```

## Selection Inputs

### ui.select(label='', options=None, value=None, multiple=False)

Dropdown selection.

```python
country = ui.select(label='Country', options=['USA', 'Canada', 'Mexico'])
role = ui.select(label='Role', options={'admin': 'Admin', 'user': 'User'})

# Multiple selection
colors = ui.select(label='Colors', options=['Red', 'Green', 'Blue'], multiple=True)
```

### ui.radio(options, value=None)

Radio button group.

```python
size = ui.radio(['S', 'M', 'L', 'XL'], value='M')
ui.radio(options, value=None).props('color=primary')
```

### ui.toggle(options, value=None)

Toggle button group.

```python
mode = ui.toggle(['Light', 'Dark', 'Auto'], value='Light')
```

### ui.checkbox(text='', value=False)

Checkbox input.

```python
agree = ui.checkbox('I agree to terms')
ui.checkbox('Remember me', value=True).props('color=primary')
```

### ui.switch(text='', value=False)

Toggle switch.

```python
dark = ui.switch('Dark Mode')
ui.switch('Enable notifications', value=True)
```

## Range Inputs

### ui.slider(min=None, max=None, value=None, step=None)

Range slider.

```python
volume = ui.slider(min=0, max=100, value=50, step=1)
ui.slider(min=0, max=100, value=50).props('label')
```

### ui.range(min=None, max=None, value=None)

Dual-thumb range slider.

```python
range_val = ui.range(min=0, max=100, value={'min': 20, 'max': 80})
```

## Specialized Inputs

### ui.color_picker(label='', value=None)

Color picker input.

```python
color = ui.color_picker(label='Pick a color')
ui.label().bind_text_from(color, 'value')
```

### ui.date(label='', value=None)

Date picker.

```python
date = ui.date(label='Select date')
date = ui.date(label='Birthday', value='2024-01-15')
```

### ui.time(label='', value=None)

Time picker.

```python
time = ui.time(label='Select time')
time = ui.time(label='Alarm', value='09:00')
```

### ui.file_upload(label='', on_upload=None, multiple=False)

File upload component.

```python
def handle_upload(e: events.UploadEventArguments):
    ui.notify(f'Uploaded: {e.name} ({e.content_type})')
    # e.content - file bytes
    # e.name - filename

ui.file_upload(label='Upload', on_upload=handle_upload, multiple=True)
ui.file_upload(label='Images only', accept='image/*', multiple=True)
```

## Common Properties

- `.value` - Get/set current value
- `.bind_value(obj, attr)` - Two-way binding
- `.bind_enabled_from(obj, attr)` - Reactive enabled state
- `.props()` - Quasar props
- `.classes()` - CSS classes
- `.on_value_change(handler)` - Value change event
- `.set_value(val)` - Programmatic update