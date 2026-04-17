# Mobile & Responsive

Quick reference for mobile features, responsive design, and touch interactions in NiceGUI.

## Responsive Design

### Breakpoint Detection

```python
# Get screen size info
screen = ui.context.client.screen
# Access in async context
# screen.width, screen.height, screen.dark
```

### Responsive Classes

```python
# Show/hide based on screen size
ui.label('Desktop only').classes('hidden md:block')
ui.label('Mobile only').classes('block md:hidden')

# Responsive width
ui.card().classes('w-full md:w-1/2 lg:w-1/3')
```

### Responsive Grid

```python
# 1 column mobile, 2 tablet, 3 desktop
with ui.grid(columns=1):
    ui.label('Item 1')
    ui.label('Item 2')

# Or with responsive
ui.row().classes('flex-col md:flex-row')
```

## Touch Gestures

### Slide Item

Swipeable list items with actions.

```python
from nicegui import ui

with ui.list().props('bordered separator'):
    # Slide left/right
    with ui.slide_item('Swipe me') as item:
        item.left('Delete', color='red', on_slide=lambda: handle_delete())
        item.right('Edit', color='green', on_slide=lambda: handle_edit())
    
    # Slide up/down
    with ui.slide_item('Swipe vertical') as item2:
        item2.top('Top', color='blue')
        item2.bottom('Bottom', color='purple')
```

### Touch Events

```python
# Handle touch events
element.on('touchstart', handler)
element.on('touchmove', handler)
element.on('touchend', handler)
```

### Pull to Refresh

```python
# Using Quasar props
ui.column().props('pull-to-refresh')
```

## Mobile Navigation

### Bottom Navigation (Quasar)

```python
# Using tabs with bottom navigation style
with ui.tabs().props('mobile flat align="justify"'):
    ui.tab('home', icon='home')
    ui.tab('favorites', icon='favorite')
    ui.tab('settings', icon='settings')
```

### Drawer Navigation (Mobile)

```python
# Hidden drawer that slides in
with ui.drawer().props('bordered').classes('w-64'):
    ui.label('Navigation Menu')
    ui.button('Home', on_click=go_home).classes('w-full')
    ui.button('Settings', on_click=go_settings).classes('w-full')

# Toggle button for mobile
ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('lg:hide')
```

### Responsive Menu

```python
# Show hamburger on mobile, buttons on desktop
with ui.row():
    ui.button(icon='menu').props('lg:hide')  # Mobile only
    with ui.row().classes('hidden lg:flex'):  # Desktop only
        ui.button('Home')
        ui.button('About')
```

## PWA Support

### Manifest Configuration

```python
ui.run(
    pwa_compatible=True,
    pwa_icon='/icon.png',
    pwa_theme_color='#ffffff'
)
```

### Service Worker

```python
# Register service worker via JavaScript
ui.add_head_html('''
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
}
</script>
''')
```

## Mobile Optimizations

### Viewport

```python
# Add viewport meta
ui.add_head_html('''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
''')
```

### Touch-Friendly Sizing

```python
# Larger touch targets
ui.button().props('size=lg')
ui.input().props('dense')

# Add padding
ui.button().classes('p-4')
ui.input().classes('p-3')
```

### Prevent Zoom

```python
ui.add_css('''
@viewport {
    zoom: 1.0;
    user-zoom: fixed;
}
''')
```

### Disable Text Selection

```python
# Prevent text selection on interactive elements
ui.button().props('no-caps')
ui.label().style('user-select: none')
```

## Mobile Patterns

### Scrollable Container

```python
with ui.column().classes('h-screen overflow-auto'):
    ui.label('Scrollable content')
    # ... long content
```

### Infinite Scroll

```python
async def load_more():
    more_data = await fetch_data()
    for item in more_data:
        ui.label(item)

# Intersection observer for infinite scroll
ui.element('div').props('v-if="showMore"')
```

### Bottom Sheet (Mobile)

```python
with ui.bottom_sheet() as sheet:
    ui.label('Bottom sheet content')
    ui.button('Close', on_click=sheet.close)
```

### Action Sheet

```python
with ui.action_sheet() as sheet:
    ui.action_sheet_item('Option 1', on_click=lambda: handle(1))
    ui.action_sheet_item('Option 2', on_click=lambda: handle(2))
    ui.action_sheet_item('Cancel', on_click=sheet.close)
```

## Dark Mode on Mobile

```python
# Auto-detect system preference
ui.run(dark=None)  # None = follow system

# Or set explicitly
ui.run(dark=True)
```

## Safe Areas

```python
# Add padding for notches/islands
ui.column().classes('safe-area-inset-top')
ui.column().classes('safe-area-inset-bottom')
ui.column().classes('safe-area-inset-left')
ui.column().classes('safe-area-inset-right')
```

## Common Mobile Issues

### Prevent Pull-to-Refresh

```python
ui.add_css('''
body {
    overscroll-behavior: contain;
}
''')
```

### Smooth Scrolling

```python
ui.add_css('''
html {
    scroll-behavior: smooth;
}
''')
```

### Disable Mobile Styles

```python
# Disable Quasar mobile detection
ui.add_css('''
.desktop-only {
    display: block;
}
.mobile-only {
    display: none;
}
''')
```

## Testing Mobile

```python
# In testing, simulate mobile viewport
async def test_mobile(user: User):
    await user.open('/')
    # With mobile viewport
    user.viewport = {'width': 375, 'height': 667}
```

## Quick Reference

```python
# Mobile-only
ui.element().classes('block lg:hidden')

# Desktop-only  
ui.element().classes('hidden lg:block')

# Tablet
ui.element().classes('hidden md:block lg:hidden')

# Touch-friendly button
ui.button().props('rounded-lg p-4 min-h-[48px]')

# Responsive card
ui.card().classes('w-full sm:w-1/2 md:w-1/3')
```