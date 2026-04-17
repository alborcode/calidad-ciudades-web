# Styling & Theming

Quick reference for styling, CSS, and theming in NiceGUI.

## Tailwind CSS

### Using .classes()

Apply Tailwind utility classes directly.

```python
ui.label('Styled').classes('text-3xl font-bold text-blue-500')
ui.button('Primary').classes('bg-blue-500 text-white px-4 py-2 rounded')

# Add/remove classes dynamically
element.classes('add-class', remove='remove-class')
```

### Common Tailwind Classes

```python
# Text
ui.label().classes('text-sm text-lg text-xl text-2xl text-3xl')
ui.label().classes('font-bold font-light font-mono')
ui.label().classes('text-center text-left text-right')
ui.label().classes('text-red-500 text-blue-700')

# Spacing
ui.column().classes('p-4 m-2 gap-2 gap-4')
ui.label().classes('mt-2 mb-4 ml-2 mr-2')

# Layout
ui.row().classes('w-full h-screen')
ui.row().classes('flex justify-center items-center')
ui.column().classes('grid grid-cols-3 gap-4')

# Colors
ui.button().classes('bg-blue-500 hover:bg-blue-700')
ui.card().classes('bg-gray-100 dark:bg-gray-800')
```

## Quasar Props

### Using .props()

Apply Quasar component properties.

```python
ui.button('Primary').props('color=primary')
ui.button('Outline').props('outline')
ui.button('Rounded').props('rounded')
ui.input().props('dense outlined')
ui.card().props('flat bordered')
```

### Common Quasar Props

```python
# Colors
ui.button().props('color=primary')
ui.button().props('color=secondary')
ui.button().props('color=accent')
ui.button().props('color=positive')
ui.button().props('color=negative')
ui.button().props('color=warning')
ui.button().props('color=info')

# Button variants
ui.button().props('flat')
ui.button().props('outline')
ui.button().props('unelevated')
ui.button().props('rounded')
ui.button().props('square')
ui.button().props('circle')

# Input styles
ui.input().props('dense outlined')
ui.input().props('filled')
ui.input().props('standout')
ui.input().props('rounded')

# Sizes
ui.button().props('size=sm')
ui.button().props('size=md')
ui.button().props('size=lg')

# States
ui.button().props('disable')
ui.button().props('loading')
ui.button().props('disable flat')
```

## Custom CSS

### ui.add_css()

Inject custom CSS into the page.

```python
ui.add_css('''
.custom-class {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
}
''')

ui.label('Custom').classes('custom-class')
```

### ui.add_head_html()

Add HTML to the document head.

```python
ui.add_head_html('''
<style>
    body { background-color: #f0f0f0; }
    .my-element { color: red; }
</style>
''')
```

### ui.add_css() for Dark Mode

```python
# Prevent white flash in dark mode
ui.add_head_html('''
<style>
body { background-color: #121212; color: white; }
</style>
''', shared=True)
```

## Dark Mode

### Page-Level Dark Mode

```python
@ui.page('/dark', dark=True)
def dark_page():
    ui.label('Dark mode enabled')
```

### Programmatic Dark Mode

```python
# Toggle dark mode
ui.dark().enable()
ui.dark().disable()
ui.dark().toggle()

# Check current state
is_dark = ui.dark().enabled()
```

### Dark Mode with Tailwind

Use Quasar's `.body--dark` class (not Tailwind's `dark:` prefix):

```python
ui.label('Adaptive text').classes('.body--dark:text-white')
ui.card().classes('.body--dark:bg-gray-800')
```

### Global Dark Mode

```python
ui.run(dark=True)  # Enable by default
```

## Theming

### Custom Color Palette

```python
ui.colors(
    primary='#555',
    secondary='#888',
    accent='#ff0000',
    dark='#121212',
    dark_page='#1a1a1a'
)

# Then use in props
ui.button().props('color=primary')
ui.button().props('color=accent')
```

### Dynamic Theming

```python
# Change theme at runtime
def set_theme(mode):
    if mode == 'dark':
        ui.colors(primary='#1a1a1a', secondary='#333')
    else:
        ui.colors(primary='#007bff', secondary='#6c757d')
    
    ui.dark().set(mode == 'dark')

ui.toggle(['Light', 'Dark'], value='Light').on_value_change(
    lambda e: set_theme(e.value)
)
```

## Responsive Design

### Breakpoint Classes

```python
# Mobile first
ui.column().classes('w-full md:w-1/2 lg:w-1/3')

# Show/hide on breakpoints
element.classes('block md:hidden')  # Hide on desktop
element.classes('hidden md:block')  # Hide on mobile
```

### Responsive Grid

```python
with ui.grid(columns=2):
    ui.label('Col 1')
    ui.label('Col 2')

# Or with responsive columns
ui.row().classes('flex-col md:flex-row')
```

## Animation

### Quasar Transitions

```python
ui.button('Animate').props('transition-show=slide-left')
ui.button('Animate').props('transition-hide=scale')
```

### CSS Animations

```python
ui.add_css('''
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
.fade-in { animation: fadeIn 1s ease-in; }
''')
ui.label('Fade In').classes('fade-in')
```

### Spinner Animation

```python
ui.spinner(size='lg').props('animation')
ui.spinner('dots')  # Different styles
```

## Common Patterns

```python
# Card with shadow
with ui.card().classes('shadow-lg p-4'):
    ...

# Centered content
with ui.column().classes('items-center justify-center h-screen'):
    ...

# Responsive image
ui.image(url).classes('w-full md:w-64')

# Hover effects
ui.button().classes('hover:bg-blue-600 transition-colors')
```