# Agent Guide - NiceGUI

Guía específica para que un Agente entienda cómo trabajar con NiceGUI en este proyecto.

## Estructura de Archivo Típica

```
proyecto/
├── main.py              # Entry point con ui.run()
├── ui/
│   ├── __init__.py
│   ├── paginas.py       # Definiciones de páginas @ui.page
│   ├── componentes.py   # Componentes reutilizables
│   └── layouts.py       # Layouts complejos
└── servicios/
    └── api.py           # Lógica de negocio
```

## Patrones del Proyecto

### Componente Simple
```python
# ui/componentes.py
from nicegui import ui

def tarjeta_titulo(titulo: str):
    with ui.card():
        ui.label(titulo).classes('text-h5')
        ui.separator()
```

### Página con Estado
```python
# ui/paginas.py
from nicegui import app, ui

@ui.page('/dashboard')
def dashboard():
    # Cargar datos del storage global
    datos = app.storage.general.get('datos', [])
    
    with ui.column():
        ui.label(f'Total: {len(datos)}')
        render_tabla(datos)

def render_tabla(datos):
    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id'},
        {'name': 'nombre', 'label': 'Nombre', 'field': 'nombre'},
    ]
    ui.table(columns=columns, rows=datos, row_key='id')
```

### API Externa con Loading
```python
async def fetch_with_loading():
    btn = ui.button('Cargar')
    btn.props('loading')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.example.com')
            datos = response.json()
            app.storage.general['datos'] = datos
            ui.notify('Datos cargados', type='positive')
    except Exception as e:
        ui.notify(f'Error: {e}', type='negative')
    finally:
        btn.props(remove='loading')
```

## Cosas a Evitar

1. **No poner ui.run() en funciones** - Debe ser al final del archivo principal
2. **No usar variables globales para estado** - Usar `app.storage`
3. **No hacer operaciones bloqueantes en handlers** - Usar `background_tasks.create()`
4. **No olvidar storage_secret** - Required para browser/user storage

## Dependencias del Proyecto

```python
# Siempre instalar
pip install nicegui

# Opcionales para este proyecto
pip install httpx pandas plotly
```
