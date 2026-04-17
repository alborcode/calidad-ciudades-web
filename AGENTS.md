# AGENTS.md - Calidad Ciudades Web

## Ejecutar la App
```bash
.venv/Scripts/python.exe -m app.main
```
Abre: http://localhost:8080

## Estructura del Proyecto
```
app/
├── main.py           # Entry point con @ui.page('/')
├── database.py        # Conexión SQLite, queries, lógica de scoring
├── models.py         # Dataclasses
├── components/       # Componentes UI reutilizables
│   ├── filters.py    # Filtros de búsqueda
│   ├── score_circle.py  # Círculo SVG de puntuación
│   ├── city_table.py    # Lista de resultados
│   └── detail_dialog.py # Ventana de detalle
└── pages/
    └── main_page.py  # Página principal
data/
└── calidad_ciudades.db  # SQLite (427 ciudades)
```

## Reglas Críticas NiceGUI
1. **No usar `ui.header()` dentro de `ui.column()`** → Error "top level layout elements cannot be nested"
2. **Handlers de click: usar `def` (sync), no `async`** → Si necesitas async, usar `async def` pero sin `await` en operaciones UI
3. **`storage_secret` obligatorio** → `ui.run(storage_secret='...')` para browser storage
4. **Importar desde venv** → `.venv/Scripts/python.exe -m app.main`

## Scoring de Ciudades
- Rango en BD: -2 (mínimo) a 18 (máximo)
- Transformación a 1-100: `((score + 2) / 20) * 99 + 1`
- Colores: Alta=#006400, Media-Alta=#228B22, Media=#FFD700, Media-Baja=#FF8C00, Baja=#DC143C

## Base de Datos
- **Path**: `data/calidad_ciudades.db`
- **Tablas clave**: `localidades`, `calidad_ciudad`, `vivienda`, `gastos`, `hospitales`, `transporte_urbano`, `cultura`
- **Verificar imports BD**:
  ```python
  .venv/Scripts/python.exe -c "from app.database import buscar_ciudades, CiudadFiltro"
  ```

## Skills Disponibles
- `.agents/skills/nicegui-skill/` → NiceGUI UI patterns y componentes
- `.agents/skills/sqlite-skill/` → SQLite queries

## Idioma
- Comentarios/docs: **español**
- Código: español o inglés (consistente)
