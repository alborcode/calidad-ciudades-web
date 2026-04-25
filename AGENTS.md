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
│   ├── filters.py    # Filtros de búsqueda (⚠️ pendiente mejorar)
│   ├── score_circle.py  # Círculo SVG de puntuación
│   ├── city_table.py    # Lista de resultados
│   └── detail_dialog.py # Ventana de detalle (✅ completado)
└── pages/
    └── main_page.py  # Página principal (⚠️ cabecera pendiente mejorar)
data/
└── calidad_ciudades.db  # SQLite (427 ciudades)
```

## Reglas Críticas NiceGUI
1. **No usar `ui.header()` dentro de `ui.column()`** → Error "top level layout elements cannot be nested"
2. **Handlers de click: usar `def` (sync), no `async`** → Si necesitas async, usar `async def` pero sin `await` en operaciones UI
3. **Importar desde venv** → `.venv/Scripts/python.exe -m app.main`
4. **Variables de entorno** → No usar `storage_secret` (no se usa app.storage en esta aplicación)

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

## Mapa (Plotly + OpenStreetMap)
- **Proveedor**: OpenStreetMap vía Plotly `scattermapbox`
- **Zoom adaptativo por zona geográfica**:
  - **Canarias** (lat < 36): zoom 5.9, centro (28.5, -15.5)
  - **Baleares** (36 ≤ lat ≤ 41, 1 ≤ lon ≤ 5): zoom 5.9, centro (39.5, 3)
  - **España peninsular** (resto): zoom 3.6, centro (40.5, -3.7)
- **Marcador**: Círculo azul (`symbol="circle"`, `size=10`, `color="blue"`)
- **Texto**: Nombre de la ciudad, 10px, posición "top center"
- **Tooltip**: Fondo azul claro (`rgba(173, 216, 230, 0.9)`), muestra Nombre, Provincia, Población
- **Contenedor**: `max-width: 100%`, `overflow: hidden` para evitar desbordamiento

## Docker para Producción
- **Imagen**: `python:3.14-slim`
- **Volumen**: `/path/en/servidor/data:/app/data` (solo BD)
- **Puerto**: 8080:8080
- **BD**: Se sube manualmente con `scp data/calidad_ciudades.db usuario@servidor:/path/to/data/`
- **Ver guía completa**: `DOCKER_DEPLOYMENT.md`

## Skills Disponibles
- `.agents/skills/nicegui-skill/` → NiceGUI UI patterns y componentes
- `.agents/skills/sqlite-skill/` → SQLite queries

## Idioma
- Comentarios/docs: **español**
- Código: español o inglés (consistente)

## Estado Actual
- ✅ Detalle de ciudad completado (UI, mapa, comparativas)
- ✅ Docker configurado para Dockploy
- ✅ Filtros del menú lateral mejorados (Costa, Metro, Aeropuerto, AVE, FEVE, UI)
- ✅ Cabecera mejorada (icono, sticky header)
- ✅ Diálogos detalle con header/footer fijos y scroll (90vh)
- ✅ Badges transporte todos estáticos (no clickeables)
