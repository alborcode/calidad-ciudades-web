# Buttons & Interactive Elements

Quick reference for buttons and interactive components in NiceGUI.

## Buttons

### ui.button(text='', on_click=None, icon=None)

Standard button.

```python
ui.button('Click me', on_click=lambda: ui.notify('Clicked!'))
ui.button(icon='refresh', on_click=refresh_data)
ui.button('Save', icon='save').props('color=primary')

# With loading state
btn = ui.button('Process')
btn.props('loading')
btn.disable()
btn.enable()
```

### ui.button_group()

Group of buttons with shared styling.

```python
with ui.button_group():
    ui.button('One', on_click=handler1)
    ui.button('Two', on_click=handler2)
    ui.button('Three', on_click=handler3)
```

### ui.icon_button(icon='', on_click=None)

Icon-only button.

```python
ui.icon_button('edit', on_click=edit_handler)
ui.icon_button('delete', on_click=delete_handler).props('color=negative')
```

## Toggle & Selection

### ui.toggle(options, value=None)

Toggle button group (segmented control).

```python
mode = ui.toggle(['Light', 'Dark', 'Auto'], value='Light')
view = ui.toggle({'grid': 'Grid', 'list': 'List'}, value='grid')
```

### ui.radio(options, value=None)

Radio button group.

```python
size = ui.radio(['S', 'M', 'L', 'XL'], value='M')
ui.radio(['Option A', 'Option B', 'Option C'])
```

### ui.segmented_button(options, value=None)

Segmented button control.

```python
view = ui.segmented_button(['List', 'Grid'], value='List')
```

## Chips

### ui.chip(text='', on_click=None, removable=False)

Chip/tag element.

```python
# Basic chip
ui.chip('Tag 1')

# Clickable chip
ui.chip('Clickable', on_click=lambda: ui.notify('Clicked!'))

# Removable chip
chip = ui.chip('Removable')
chip.on('remove', lambda: chip.delete())

# Icon chip
ui.chip('Filter', icon='filter').props('clickable')
```

### ui.chip_group()

Container for multiple chips.

```python
with ui.chip_group():
    for tag in tags:
        ui.chip(tag)
```

## Action Components

### ui.menu()

Dropdown menu.

```python
with ui.button(icon='menu'):
    with ui.menu():
        ui.menu_item('New', icon='add', on_click=new_handler)
        ui.menu_item('Open', icon='folder_open')
        ui.separator()
        ui.menu_item('Exit', icon='exit_to_app')
```

### ui.context_menu()

Right-click context menu.

```python
element = ui.label('Right-click me')
with element:
    with ui.context_menu():
        ui.menu_item('Copy', icon='content_copy')
        ui.menu_item('Paste', icon='content_paste')
```

### ui.split_panel()

Resizable split panel.

```python
with ui.split_panel():
    with ui.pane():
        ui.label('Left panel')
    with ui.pane():
        ui.label('Right panel')
```

## Loading & Progress

### ui.spinner(size='lg')

Loading spinner.

```python
ui.spinner(size='xl', color='red')
ui.spinner().props('size=50px color=primary')
```

### ui.progress(value=None, max=100)

Progress bar.

```python
progress = ui.progress(value=50, max=100)
ui.progress(value=75).props('reverse color=positive')
```

### ui.linear_progress(value=None, max=100)

Linear progress bar.

```python
ui.linear_progress(value=30, max=100)
```

### ui.circular_progress(value=None, max=100)

Circular progress indicator.

```python
ui.circular_progress(value=60, max=100).props('size=50px')
```

## Common Props

```python
# Button variants
ui.button('Primary').props('color=primary')
ui.button('Secondary').props('color=secondary')
ui.button('Outline').props('outline')
ui.button('Flat').props('flat')
ui.button('Rounded').props('rounded')
ui.button('Square').props('square')

# Sizes
ui.button('Small').props('size=sm')
ui.button('Medium').props('size=md')
ui.button('Large').props('size=lg')

# States
ui.button('Loading').props('loading')
ui.button('Disable').props('disable')
```

## Icon Reference

Use Quasar icon names:
- Material icons: 'home', 'settings', 'edit', 'delete', 'add', 'save'
- FontAwesome: 'fas fa-home'
- Custom: icon='mdi-home'

```python
ui.button(icon='home', text='Home')
ui.icon_button('settings').props('color=grey-8')