# MEMORY.md - Calidad Ciudades Web

## Estado Actual
- Última sesión: 2026-04-25
- Tareas completadas:
  - 01 - Crear estructura proyecto base - **OpenCode/minimax-m2.5**
  - 02 - Implementar filtros de búsqueda - **OpenCode/minimax-m2.5**
  - 03 - Implementar tabla resultados con círculos - **OpenCode/minimax-m2.5**
  - 04 - Implementar diálogo detalle con mapas - **OpenCode/minimax-m2.5**
  - 05 - Integrar Plotly para mapas - **OpenCode/minimax-m2.5**
  - 06 - Añadir helper compare_to_national y reemplazar comparadores en detail_dialog - **OpenAgent/gpt-5-mini**
  - 07 - Hacer app responsiva para PC y móvil - **OpenCode/minimax-m2.5**
  - 08 - Modificar colores en cajas Paro, Renta y Seguridad en detail_dialog - **OpenAgent/qwen3.5-plus**
  - 09 - Corregir claves datos_nacionales para Paro y Seguridad - **OpenAgent/qwen3.5-plus**
  - 10 - Mejorar marcador y tooltip del mapa en Ubicación - **OpenAgent/qwen3.5-plus**
  - 11 - Ajustar tamaño de fuente del nombre en el mapa - **OpenAgent/qwen3.5-plus**
  - 12 - Modificar estructura del diálogo con cabecera y pie fijos + scroll - **OpenAgent/qwen3.5-plus**
  - 13 - Configuración Docker para Dockploy - **OpenAgent/qwen3.5-plus**
  - 14 - Actualizar documentación DOCKER_DEPLOYMENT.md, MEMORY.md, PLAN.md, AGENTS.md - **OpenAgent/qwen3.5-plus**
  - 15 - Crear README.md completo con documentación detallada de filtros y ventanas - **OpenAgent/qwen3.5-plus**
  - 16 - Mejorar filtros menú lateral (Costa, Metro, Aeropuerto, AVE, FEVE, UI) - **OpenAgent/qwen3.5-plus**
  - 17 - Mejorar cabecera (icono, sticky header) - **OpenAgent/qwen3.5-plus**
  - 18 - Mejorar diálogos detalle (header/footer fijos, scroll, 90vh) - **OpenAgent/qwen3.5-plus**
  - 19 - Corregir bibliotecas (usa numero_bibliotecas de tabla educacion) - **OpenAgent/qwen3.5-plus**
  - 20 - Actualizar badges transporte (todos estáticos, añadir FEVE) - **OpenAgent/qwen3.5-plus**
- Tarea en progreso: Ninguna

## Siguiente Paso
- Opcional: Añadir tests unitarios para app/utils/visuals.py

## Decisiones Tomadas
- NiceGUI como framework UI (web app Python)
- Plotly con OpenStreetMap para visualización de mapas
- SQLite con la BD existente
- **Mapa**: Zoom adaptativo según zona geográfica (ver AGENTS.md para detalles)
- Centro mapa automático: España (40.5, -3.7), Canarias (28.5, -15.5), Baleares (39.5, 3)
- Fórmula scoring: ((score + 2) / 20) * 99 + 1 → escala 1-100
- Marcador mapa: círculo azul con texto nombre (fuente 10px)
- Tooltip mapa: fondo azul claro, muestra Nombre, Provincia, Población (no Lat/Lon)
- Diálogo detalle: cabecera fija + cuerpo con scroll + pie fijo (85vh altura máx)
- Docker: Solo BD se monta como volumen, resto de archivos data/ no necesarios en producción

## Archivos Clave
- `app/main.py` - Entry point
- `app/database.py` - Queries SQLite
- `app/components/detail_dialog.py` - Ventana detalle con mapa (completado ✅)
- `app/components/score_circle.py` - Círculo puntuación SVG
- `app/components/filters.py` - Filtros búsqueda (pendiente mejorar)
- `app/components/city_table.py` - Tabla resultados
- `app/utils/visuals.py` - Helpers visuales comparativos
- `Dockerfile` - Configuración Docker para Dockploy
- `DOCKER_DEPLOYMENT.md` - Guía despliegue producción

## Contexto Importante
- BD: `data/calidad_ciudades.db` (427 ciudades)
- Rango scoring BD: -2 a 18
- Paquetes nuevos: plotly, kaleido, numpy
- NiceGUI 3.10.0
- Python 3.14
- **Datos nacionales en `datos_nacionales`**:
  - `TASA_PARO_NACIONAL` = 5.11% (calculado de la BD)
  - `TASA_CRIMINALIDAD_NACIONAL` = 40.4
  - `TASA_ROBOS_NACIONAL` = 1.26
  - `Renta bruta media por persona` = 16.712€
  - `Renta neta media por persona` = 13.268€
- **Docker**: Volumen `data:/app/data` solo para BD, no incluir CSV/XLS en producción

## Tareas Pendientes
- ✅ Mejorar filtros del menú lateral (izquierda) - UI/UX (completado)
- ✅ Mejorar cabecera de la aplicación - UI/UX (completado)
- ✅ Mejorar diálogos detalle (header/footer fijos) - UI/UX (completado)
- ✅ Actualizar badges transporte (todos estáticos, añadir FEVE) - UI/UX (completado)
- ⬜ Opcional: Añadir tests unitarios

## Tracking de Uso
- Total tareas completadas: 20
- Agentes utilizados: OpenCode, OpenAgent
- Modelos utilizados: minimax-m2.5, gpt-5-mini, qwen3.5-plus
