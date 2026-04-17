# MEMORY.md - Calidad Ciudades Web

## Estado Actual
- Última sesión: 2026-04-17
- Tareas completadas:
  - 01 - Crear estructura proyecto base - **OpenCode/minimax-m2.5**
  - 02 - Implementar filtros de búsqueda - **OpenCode/minimax-m2.5**
  - 03 - Implementar tabla resultados con círculos - **OpenCode/minimax-m2.5**
  - 04 - Implementar diálogo detalle con mapas - **OpenCode/minimax-m2.5**
  - 05 - Integrar Plotly para mapas - **OpenCode/minimax-m2.5**

## Siguiente Paso
- Mantenimiento y mejoras según feedback de usuario

## Decisiones Tomadas
- NiceGUI como framework UI (web app Python)
- Plotly con OpenStreetMap para visualización de mapas
- SQLite con la BD existente
- Zoom adaptativo: España 3.6, Canarias/Baleares 5.9
- Centro mapa: España (40.5, -3.7), Canarias (28.5, -15.5), Baleares (39.5, 3)
- Fórmula scoring: ((score + 2) / 20) * 99 + 1 → escala 1-100

## Archivos Clave
- `app/main.py` - Entry point
- `app/database.py` - Queries SQLite
- `app/components/detail_dialog.py` - Ventana detalle con mapa
- `app/components/score_circle.py` - Círculo puntuación SVG
- `app/components/filters.py` - Filtros búsqueda
- `app/components/city_table.py` - Tabla resultados

## Contexto Importante
- BD: `data/calidad_ciudades.db` (427 ciudades)
- Rango scoring BD: -2 a 18
- Paquetes nuevos: plotly, kaleido, numpy
- NiceGUI 3.10.0
- Python 3.14

## Tracking de Uso
- Total tareas completadas: 5
- Agentes utilizados: OpenCode
- Modelos utilizados: minimax-m2.5
