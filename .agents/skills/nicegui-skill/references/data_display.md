# Data Display

Quick reference for data display elements in NiceGUI.

## Tables

### ui.table(columns, rows, row_key=None, ...)

Data table with sorting, selection, pagination.

```python
columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
    {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
    {'name': 'email', 'label': 'Email', 'field': 'email'},
]
rows = [
    {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
    {'name': 'Bob', 'age': 25, 'email': 'bob@example.com'},
]

table = ui.table(columns=columns, rows=rows, row_key='name')
```

### Table with Selection

```python
# Single selection
table = ui.table(columns, rows, row_key='name', selection='single')

# Multiple selection
table = ui.table(columns, rows, row_key='name', selection='multiple')

# Get selected rows
selected = table.selected
```

### Table with Custom Cells

```python
columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name'},
    {'name': 'action', 'label': 'Action', 'align': 'center'},
]
rows = [{'name': 'Alice'}, {'name': 'Bob'}]

table = ui.table(columns=columns, rows=rows)
with table.add_slot('body-cell-action'):
    with table.cell('action'):
        ui.button('Edit').props('flat').on('click', handler)
```

### Table as Grid/Cards

```python
table = ui.table(columns, rows, row_key='name').props('grid')
with table.add_slot('item'):
    with ui.card().tight().props('flat bordered').classes('m-1'):
        ui.label().props(':innerHTML=props.row.name')
```

## Lists

### ui.list()

List container.

```python
with ui.list():
    ui.item('Item 1')
    ui.item('Item 2').on('click', handler)
    ui.item('Item 3')
```

### ui.item()

List item.

```python
with ui.list():
    with ui.item():
        with ui.item_section().props('avatar'):
            ui.icon('person')
        with ui.item_section():
            ui.item_label('Title')
            ui.item_label('Subtitle').props('caption')
```

### ui.item_section()

Section within list item (avatar, content, side).

```python
with ui.item():
    with ui.item_section().props('avatar'):
        ui.avatar('JD', text_color='white', color='primary')
    with ui.item_section():
        ui.item_label('John Doe')
        ui.item_label('john@example.com').props('caption')
    with ui.item_section().props('side'):
        ui.badge('New')
```

### ui.item_label()

Label within item section.

## Trees

### ui.tree()

Hierarchical tree display.

```python
nodes = {
    'root': {
        'label': 'Root',
        'children': [
            {'label': 'Child 1'},
            {'label': 'Child 2'},
        ]
    }
}
ui.tree(nodes, label_key='label')
```

### ui.tree_node()

Tree node item.

```python
with ui.tree(['Item 1', 'Item 2']):
    with ui.tree_node('Item 1'):
        ui.label('Sub-item A')
        ui.label('Sub-item B')
```

## Pagination

### ui.pagination(page=1, max_page=1, direction_links=True, boundary_links=False)

Pagination controls.

```python
paginator = ui.pagination(page=1, max_page=10)
paginator.on_value_change(lambda e: load_page(e.value))
```

## Breadcrumbs

### ui.breadcrumbs()

Breadcrumb navigation.

```python
ui.breadcrumbs([
    {'text': 'Home', 'to': '/'},
    {'text': 'Products', 'to': '/products'},
    {'text': 'Details', 'to': None},  # Current (no link)
])
```

## Timeline

### ui.timeline()

Vertical timeline display.

```python
with ui.timeline(sided=True):
    with ui.timeline_entry(title='Event 1', subtitle='2024-01-01'):
        ui.label('Description 1')
    with ui.timeline_entry(title='Event 2', subtitle='2024-02-01'):
        ui.label('Description 2')
```

## Chat & Messages

### ui.chat_message()

Chat message bubble.

```python
with ui.chat_message(name='Alice', text='Hello!', stamp='10:30'):
    ui.avatar('A', text_color='white', color='blue')

# Sent by user
with ui.chat_message(avatar='https://example.com/me.png', sent=True):
    ui.label('My message')
```

### ui.chat()

Chat container.

```python
with ui.chat():
    with ui.chat_message(name='Bot', text='Hello!'):
```

## Badge & Tag

### ui.badge(text='', color=None, icon=None)

Badge/label indicator.

```python
ui.badge('New', color='green')
ui.badge('5', color='red', icon='notifications')
ui.button('Inbox').props('stack')
with ui.button():
    ui.badge('3', color='red').props('floating')
```

### ui.caption()

Caption text.

```python
with ui.card():
    ui.label('Title')
    ui.caption('Subtitle text')
```

## Common Properties

```python
# Table styling
ui.table().props('flat bordered')
ui.table().props('dense rows')
ui.table().props('dark')

# Selection mode
ui.table(selection='single')
ui.table(selection='multiple')

# Pagination
ui.table(pagination=20)  # Rows per page
```