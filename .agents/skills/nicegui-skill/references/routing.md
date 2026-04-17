# Navigation & Routing

Quick reference for page routing and navigation in NiceGUI.

## Page Decorator

### @ui.page(path, dark=False, title=None, favicon=None, refresh=None)

Define a page route.

```python
@ui.page('/')
def home():
    ui.label('Welcome Home')

@ui.page('/about')
def about():
    ui.label('About Us')

@ui.page('/user/{user_id}')
def user_profile(user_id):
    ui.label(f'User ID: {user_id}')
    # user_id is available from URL

@ui.page('/products/{category}/{product_id}')
def product(category, product_id):
    ui.label(f'Category: {category}, Product: {product_id}')
```

### Page with Options

```python
@ui.page('/admin', dark=True, title='Admin Panel')
def admin_page():
    ui.label('Admin Area')
```

## Navigation Links

### ui.link(text, target, new_tab=False)

Create links between pages.

```python
ui.link('Go to About', '/about')
ui.link('Go to Home', home)  # Using function reference
ui.link('External', 'https://example.com', new_tab=True)
```

### ui.button(..., to=path)

Button with navigation.

```python
ui.button('Go Home', on_click=lambda: ui.navigate.to('/'))
```

## Sub-Pages (SPA)

### ui.sub_pages(pages, *)

Container for SPA-like sub-page navigation.

```python
def root():
    ui.label(f'Root ID: {id}')
    ui.separator()
    ui.sub_pages({'/': main, '/other': other})

def main():
    ui.label('Main page')
    ui.link('Go to other', '/other')

def other():
    ui.label('Other page')
    ui.link('Go main', '/')

ui.run(root)
```

### ui.navigate

Programmatic navigation.

```python
from nicegui import ui

ui.button('Home', on_click=lambda: ui.navigate.to('/'))
ui.button('Back', on_click=lambda: ui.navigate.back())
ui.button('Forward', on_click=lambda: ui.navigate.forward())
```

## URL Parameters

### Access Parameters

```python
@ui.page('/user/{user_id}')
def user_page(user_id):
    # Access query parameters
    page = ui.context.params.get('page', 1)
    
    # Access all parameters
    all_params = dict(ui.context.params)
```

### Query Strings

```python
@ui.page('/search')
def search():
    query = ui.context.query.get('q', '')
    page = ui.context.query.get('page', 1)
```

## Breadcrumbs Navigation

```python
ui.breadcrumbs([
    {'text': 'Home', 'to': '/'},
    {'text': 'Products', 'to': '/products'},
    {'text': 'Details', 'to': None},
])
```

## Tab Navigation

```python
with ui.tabs() as tabs:
    ui.tab('Overview')
    ui.tab('Details')

with ui.tab_panels(tabs, value='Overview'):
    with ui.tab_panel('Overview'):
        ui.label('Overview content')
    with ui.tab_panel('Details'):
        ui.label('Details content')
```

## Keyboard Navigation

### ui.keyboard()

Global keyboard event handler.

```python
ui.keyboard().on('key', handler)
ui.keyboard().on('keydown.ctrl.c', handler)
```

```python
# Prevent default
ui.label('Select all disabled')
ui.keyboard().on('key', handler, js_handler='''
    (e) => {
        if (e.key === 'a' && (e.ctrlKey || e.metaKey)) {
            emit(e);
            e.event.preventDefault();
        }
    }
''')
```

## URL Utilities

```python
from nicegui import ui

# Get current URL
current_url = ui.context.uri

# Get client info
client = ui.context.client

# Wait for connection
await ui.context.client.connected()
```

## OpenAPI Documentation

```python
ui.run(endpoint_documentation='render')  # Show OpenAPI docs
ui.run(endpoint_documentation='page')   # As separate page
ui.run(endpoint_documentation=False)    # Disable
```