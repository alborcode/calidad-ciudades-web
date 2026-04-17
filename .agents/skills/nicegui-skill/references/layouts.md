# Layout Containers

Quick reference for layout and container elements in NiceGUI.

## Basic Containers

### ui.row(wrap=True, align_items=None)

Horizontal row container.

```python
with ui.row():
    ui.label('Item 1')
    ui.label('Item 2')
    ui.label('Item 3')

# Wrap disabled
with ui.row(wrap=False):
    ...

# Alignment
with ui.row(align_items='center'):
    ...
```

### ui.column()

Vertical column container.

```python
with ui.column():
    ui.label('First')
    ui.label('Second')
    ui.label('Third')
```

### ui.grid(columns=None)

Grid layout.

```python
# 3 columns
with ui.grid(columns=3):
    ui.label('1')
    ui.label('2')
    ui.label('3')

# Responsive
with ui.grid(columns=2):
    ui.label('Col 1')
    ui.label('Col 2')
```

## Cards

### ui.card(tight=False)

Card container with shadow and padding.

```python
with ui.card():
    ui.label('Card content')
    ui.button('Action')

# Tight (no padding)
with ui.card().tight():
    ...
```

### ui.card_section()

Section within a card.

```python
with ui.card():
    with ui.card_section():
        ui.label('Section 1')
    with ui.card_section():
        ui.label('Section 2')
```

### ui.card_actions()

Actions area at bottom of card.

```python
with ui.card():
    ui.label('Content')
    with ui.card_actions():
        ui.button('Cancel')
        ui.button('Confirm').props('color=primary')
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

### ui.dialog().props()

Dialog with backdrop.

```python
with ui.dialog().props('backdrop-filter="blur(8px)"') as d:
    ui.label('Press ESC to close')
```

## Drawers

### ui.drawer()

Side drawer panel.

```python
# Left drawer
with ui.drawer().classes('bg-grey-2'):
    ui.label('Drawer content')

# Right drawer
with ui.drawer(side='right').classes('bg-grey-2'):
    ...

# Toggle
drawer = ui.drawer()
ui.button('Toggle', on_click=lambda: drawer.toggle())
```

### ui.left_drawer()

Left-side drawer shortcut.

```python
with ui.left_drawer().classes('bg-blue-1'):
    ui.label('Navigation')
```

## Tabs

### ui.tabs() / ui.tab()

Tab navigation.

```python
with ui.tabs() as tabs:
    ui.tab('Overview')
    ui.tab('Details')
    ui.tab('Settings')
```

### ui.tab_panels() / ui.tab_panel()

Tab content panels.

```python
with ui.tabs() as tabs:
    t1 = ui.tab('One')
    t2 = ui.tab('Two')

with ui.tab_panels(tabs, value=t1):
    with ui.tab_panel(t1):
        ui.label('Panel 1 content')
    with ui.tab_panel(t2):
        ui.label('Panel 2 content')
```

## Carousel

### ui.carousel(animated=False, arrows=False, navigation=False)

Image/content carousel.

```python
with ui.carousel(animated=True, arrows=True, navigation=True).props('height=200px'):
    with ui.carousel_slide():
        ui.image('https://picsum.photos/id/1/400/200')
    with ui.carousel_slide():
        ui.image('https://picsum.photos/id/2/400/200')
    with ui.carousel_slide():
        ui.image('https://picsum.photos/id/3/400/200')
```

## Splitter

### ui.splitter()

Resizable panel splitter.

```python
with ui.splitter() as splitter:
    with splitter.pane():
        ui.label('Left')
    with splitter.pane():
        ui.label('Right')
```

## Masonry Layout

### Tailwind Masonry

```python
with ui.element('div').classes('columns-3 w-full gap-2'):
    for i, height in enumerate([50, 150, 100, 80, 120, 60]):
        with ui.card().classes(f'mb-2 p-2 h-[{height}px] break-inside-avoid'):
            ui.label(f'Card {i+1}')
```

## Common Classes

```python
# Spacing
ui.row().classes('gap-2')
ui.column().classes('gap-4 p-4')

# Alignment
ui.row().classes('justify-center items-center')
ui.column().classes('items-center')

# Responsive
ui.column().classes('w-full md:w-1/2 lg:w-1/3')
```

## Element Factory

### ui.element(tag)

Create custom HTML element.

```python
ui.element('div').classes('container')
ui.element('span').style('color: red')
ui.element('hr').props('q-my-lg')
```