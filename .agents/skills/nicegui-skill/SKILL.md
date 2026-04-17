# NiceGUI Skill

## Agent Quick Start

1. **Importar**: `from nicegui import ui`
2. **Crear UI**: Añadir elementos al layout
3. **Ejecutar**: `ui.run()` al final

```python
from nicegui import ui

ui.label('Hello, NiceGUI!')
ui.button('Click me', on_click=lambda: ui.notify('Clicked!'))

ui.run()
```

## When to Use
- **Rapid prototyping** of web UIs in Python
- **Data dashboards** and monitoring interfaces
- **Simple web apps** without React/JavaScript knowledge
- **ML/AI interfaces** for models and visualizations
- **IoT dashboards** for device monitoring
- **Replacing Streamlit** with more control and better performance

## Gotchas (Errores Frecuentes)

### Olvidar `await` en async
```python
# ERROR - Operation no ejecutará correctamente
async def fetch():
    ui.notify('Loading...')
    data = api.get()  # Sin await!

# CORRECTO
async def fetch():
    ui.notify('Loading...')
    data = await api.get()
```

### bind_text_from vs bind_value
```python
# bind_text_from: source → UI (one-way)
label.bind_text_from(input, 'value')

# bind_value: source ↔ UI (two-way)
input.bind_value(app_state, 'field')
```

### Estado no persiste entre refreshes
```python
# ERROR - state se resetea en cada refresh
count = 0
@ui.refreshable
def counter():
    global count
    ui.label(str(count))

# CORRECTO - usar app.storage o dict global
count = {'value': 0}
@ui.refreshable
def counter():
    ui.label(str(count['value']))
```

### storage_secret requerido
```python
# ERROR - browser/user storage fallará
ui.run()

# CORRECTO
ui.run(storage_secret='mi-secreto-123')
```

## Decision Tree

| Necesidad | Recomendación |
|-----------|---------------|
| Tabla simple con sorting/pagination | `ui.table` |
| Tabla avanzada con filtros/excel | `ui.aggrid` |
| Mostrar dialogo awaitable | `ui.dialog` + `await dialog` |
| Sidebar persistente | `ui.drawer` |
| Datos en tiempo real | `@app.timer` + refreshable |
| Estado compartido entre páginas | `app.storage.general` |
| Estado por usuario | `app.storage.user` |
| Navegación SPA | `ui.sub_pages` |
|async operation larga | `background_tasks.create()` |

## Core Concepts

### 1. Basic Structure
```python
from nicegui import ui

ui.label('Hello, NiceGUI!')
ui.button('Click me', on_click=lambda: ui.notify('Clicked!'))

ui.run()
```

### 2. UI Elements (Built on Quasar Framework)
- **Text Elements**: `ui.label`, `ui.html`, `ui.markdown`
- **Inputs**: `ui.input`, `ui.textarea`, `ui.number`, `ui.select`, `ui.checkbox`, `ui.switch`, `ui.slider`, `ui.color_picker`
- **Buttons**: `ui.button`, `ui.toggle`, `ui.radio`, `ui.chip`
- **Data Display**: `ui.table`, `ui.card`, `ui.list`, `ui.carousel`
- **Visualization**: `ui.chart` (Plotly), `ui.progress`, `ui.spinner`
- **Layout**: `ui.row`, `ui.column`, `ui.grid`, `ui.card`, `ui.dialog`, `ui.drawer`

### 3. Reactivity System
- **Direct Property Access**: `element.value`, `element.text`
- **Event Handling**: `element.on('click', handler)` 
- **Refreshable Components**: `@ui.refreshable` decorator
- **State Management**: `ui.state(initial_value)`

### 4. Page Routing
```python
@ui.page('/home')
def home_page():
    ui.label('Welcome Home')

@ui.page('/about')
def about_page():
    ui.label('About Us')

ui.run()
```

### 5. Deployment
- Built on **Uvicorn** (ASGI server)
- Production: `ui.run(reload=False, port=8080)`
- SSL: Pass cert/key to ui.run()
- Reverse proxy: Traefik, NGINX

## Installation
```bash
pip install nicegui
```

## Execution
```bash
python main.py
# Opens at http://localhost:8080
```

## Key Features
- Auto-reload during development
- Tailwind CSS support (experimental)
- Client-side JavaScript execution
- WebSocket-based communication
- OpenAPI documentation auto-generation
- Dark mode support
- Responsive design out of the box

## Quick Start
```python
from nicegui import ui

# Simple interactive app
name = ui.input(label='Your name')
ui.button('Greet', on_click=lambda: ui.notify(f'Hello, {name.value}!'))

ui.run()
```

## Important Patterns

### Dialogs (awaitable)
```python
with ui.dialog() as dialog, ui.card():
    ui.label('Confirm?')
    ui.button('Yes', on_click=lambda: dialog.submit(True))
    ui.button('No', on_click=lambda: dialog.submit(False))

async def show():
    result = await dialog
    ui.notify(f'Result: {result}')

ui.button('Open', on_click=show)
```

### Custom JavaScript
```python
ui.button('Copy').on('click', js_handler='''
    () => navigator.clipboard.writeText("Hello!")
''')
```

## Reference Files
- `elements.md` - Text elements (label, html, markdown, code)
- `inputs.md` - Input controls (input, textarea, number, select, checkbox, etc.) → **Usar para formularios**
- `buttons.md` - Buttons and interactive elements
- `layouts.md` - Layout containers (row, column, card, dialog, drawer, etc.)
- `data_display.md` - Data display (table, list, tree, timeline, etc.) → **Tablas: ver aquí**
- `visualization.md` - Charts and visualization (Plotly, ECharts, images, video)
- `routing.md` - Page routing and navigation → **Páginas múltiples: ver aquí**
- `events.md` - Event handling and reactivity → **Liga con async.md para operaciones async**
- `dialogs.md` - Dialogs and notifications
- `deployment.md` - Deployment and configuration
- `styling.md` - Styling, Tailwind CSS, Quasar props, dark mode, theming
- `async.md` - Async programming, background tasks, timers, HTTP requests → **Liga con events.md**
- `storage.md` - App storage (browser, user, general), cookies, state management → **Estado: ver aquí**
- `testing.md` - Testing with User fixture, screen, pytest
- `mobile.md` - Mobile features, responsive design, touch gestures, PWA
- `api.md` - FastAPI/Flask integration, external APIs, WebSocket communication
- `agent_guide.md` - **GUÍA PARA AGENTES** - Estructura, patrones, gotchas del proyecto

## Spanish Examples (Para Este Proyecto)

```python
from nicegui import ui

# Etiqueta de texto
ui.label('Bienvenido al sistema')

# Input con validación
nombre = ui.input(label='Nombre', placeholder='Ingrese su nombre')

# Botón con acción
ui.button('Guardar', on_click=guardar_datos).props('color=primary')

# Tabla de datos
columnas = [
    {'name': 'id', 'label': 'ID', 'field': 'id'},
    {'name': 'nombre', 'label': 'Nombre', 'field': 'nombre'},
]
filas = [{'id': 1, 'nombre': 'Alice'}, {'id': 2, 'nombre': 'Bob'}]
ui.table(columns=columnas, rows=filas, row_key='id')

# Diálogo de confirmación
with ui.dialog() as dialogo, ui.card():
    ui.label('¿Confirmar acción?')
    with ui.row():
        ui.button('Sí', on_click=lambda: dialogo.submit(True))
        ui.button('No', on_click=lambda: dialogo.submit(False))

async def confirmar():
    resultado = await dialogo
    ui.notify(f'Resultado: {resultado}')

ui.button('Abrir', on_click=confirmar)

# Estado global (persistente)
app.storage.general['datos'] = []

# Timer para actualización automática
@app.timer(interval=60.0)  # Cada 60 segundos
def actualizar_datos():
    datos = obtener_datos_nuevos()
    app.storage.general['datos'] = datos
    tabla.refresh()
```

## Repository
- GitHub: https://github.com/zauberzeug/nicegui
- Documentation: https://nicegui.io/documentation
- Stars: 15.5k+

## Related Skills

- [/pythonista-typing](../pythonista-typing/SKILL.md) - Pydantic models for UI data
- [/pythonista-testing](../pythonista-testing/SKILL.md) - Testing controllers
- [/pythonista-async](../pythonista-async/SKILL.md) - Async UI patterns
- [/pythonista-patterning](../pythonista-patterning/SKILL.md) - Component reuse patterns
- [/pythonista-debugging](../pythonista-debugging/SKILL.md) - Debugging async issues
- [/pythonista-reviewing](../pythonista-reviewing/SKILL.md) - Test code review