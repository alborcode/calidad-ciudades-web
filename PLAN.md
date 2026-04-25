# PLAN.md - Calidad Ciudades Web

## Objetivo
Crear una aplicación web con NiceGUI que permita filtrar y visualizar ciudades españolas según su calidad de vida, basándose en datos de la base de datos SQLite `data/calidad_ciudades.db`.

---

## 1. Análisis de la Base de Datos

### Tablas Principales
| Tabla | Descripción | Clave foránea |
|-------|-------------|---------------|
| `localidades` | Datos básicos de localidades | `id` |
| `calidad_ciudad` | Puntuación y categoría de calidad | `localidad_id` |
| `vivienda` | Precios de alquiler | `localidad_id` |
| `gastos` | Gastos de alimentación (codigo '01') | `localidad_id` |
| `hospitales` | Número de hospitales | `localidad_id` |
| `transporte_urbano` | Metro, autobús, tranvía | `localidad_id` |
| `cultura` | Cines, teatros, museos | `localidad_id` |
| `costa` | Si es costa (nota_costa) | `localidad_id` |
| `param_comunidades` | Comunidades autónomas | `codigo_comunidad` |
| `param_provincias` | Provincias | `codigo_provincia` |
| `param_municipios` | Municipios | `codigo_ine` |
| `datos_nacionales` | Medias nacionales | `tipo` |
| `datos_comunidades` | Medias por comunidad | `codigo_comunidad`, `tipo` |
| `datos_provincias` | Medias por provincia | `codigo_provincia`, `tipo` |

### Esquema de Scoring
```
Alta Calidad    ≥ 15 puntos
Media-Alta      10-14 puntos
Media            5-9 puntos
Media-Baja       1-4 puntos
Baja Calidad    ≤ 0 puntos
```

---

## 2. Arquitectura de la Aplicación

### Estructura de Archivos
```
calidad-ciudades-web/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point, routing
│   ├── database.py          # Conexión SQLite y queries
│   ├── models.py            # Modelos de datos
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── main_page.py     # Página principal con filtros y tabla
│   │   └── detail_page.py   # Ventana de detalle (diálogo)
│   └── components/
│       ├── __init__.py
│       ├── filters.py       # Componente de filtros
│       ├── city_table.py    # Tabla de resultados
│       ├── score_circle.py  # Círculo de puntuación
│       └── detail_dialog.py  # Diálogo de detalle
├── data/
│   └── calidad_ciudades.db  # Base de datos
├── tests/
│   └── test_app.py
├── RULES.md
├── PLAN.md
└── requirements.txt
```

---

## 3. Funcionalidades

### 3.1 Filtros de Búsqueda
| Filtro | Tipo | Tabla/Columna | Lógica |
|--------|------|---------------|--------|
| Precio alquiler máximo | `ui.number` (opcional) | `vivienda.precio_alquiler` | `<=` valor o cualquier valor si vacío |
| Gasto alimentación máximo | `ui.number` (opcional) | `gastos.gasto_mensual` (codigo='01') | `<=` valor o cualquier valor si vacío |
| Tiene cines | `ui.checkbox` | `cultura.num_salas_cine > 0` | Marcado = TRUE, desmarcado = cualquier valor |
| Tiene teatros | `ui.checkbox` | `cultura.num_salas_teatro > 0` | Marcado = TRUE, desmarcado = cualquier valor |
| Tiene museos | `ui.checkbox` | `cultura.num_museos > 0` | Marcado = TRUE, desmarcado = cualquier valor |
| Es de costa | `ui.checkbox` | `calidad_ciudad.nota_costa = 1` | Marcado = TRUE, desmarcado = cualquier valor |
| Tiene transporte urbano | `ui.checkbox` | `transporte_urbano` (tiene_metro=1 OR tiene_autobus_municipal=1 OR tiene_tranvia=1) | Marcado = TRUE, desmarcado = cualquier valor |
| Tiene hospital | `ui.checkbox` | `hospitales.num_hospitales_total > 0` | Marcado = TRUE, desmarcado = cualquier valor |
| Tiene universidad | `ui.checkbox` | `calidad_ciudad.nota_universidad > 0` | Marcado = TRUE, desmarcado = cualquier valor |

### 3.2 Tabla de Resultados
- **Ordenación**: Por puntuación (score) DESC
- **Columnas visibles**:
  - Círculo de puntuación (1-100)
  - Nombre localidad
  - Provincia
  - Comunidad Autónoma
  - Categoría (Alta/Media-Alta/Media/Media-Baja/Baja)

### 3.3 Círculo de Puntuación
**Fórmula de transformación**:
```python
# Normalizar puntuación de -N a +M → 1-100
if puntuacion < 0:
    puntuacion_normalizada = max(1, puntuacion + 20)  # Ej: -10 → 10, -20 → 1
else:
    puntuacion_normalizada = puntuacion + 20  # Ej: 0 → 20, 15 → 35

# Extrapolar a 1-100 usando el rango已知
# Scoring rango: -20 a 35 (aproximado)
puntuacion_100 = min(100, max(1, puntuacion_normalizada * 2))
```

**Colores según categoría**:
| Categoría | Color |
|-----------|-------|
| Alta Calidad | Verde oscuro (`#006400`) |
| Media-Alta | Verde claro (`#228B22`) |
| Media | Amarillo (`#FFD700`) |
| Media-Baja | Naranja (`#FF8C00`) |
| Baja Calidad | Rojo (`#DC143C`) |

### 3.4 Ventana de Detalle
Al pulsar en una localidad, abrir un `ui.dialog` con:
- **Encabezado**: Nombre localidad, provincia, comunidad
- **Puntuación**: Círculo con nota 1-100 y color según categoría
- **Datos de la localidad** (todos los disponibles):
  - Población
  - Coordenadas (latitud, longitud, altitud)
  - Datos de vivienda (precio alquiler, m², variación)
  - Gastos (alimentación, total)
  - Transporte (AVE, cercanías, metro, tranvía, autobús, aeropuerto)
  - Transporte urbano (metro, autobús municipal, tranvía)
  - Hospitales
  - Universidad
  - Cultura (cines, teatros, museos)
  - Costa
  - Clima
  - Zonas verdes
  - Calidad del aire
  - Educación (institutos, colegios, bibliotecas)
  - Administración
  - Paro
  - Renta
  - Delitos
  - Tiempos de desplazamiento
- **Comparativas** (si existen en datos_comunidades/datos_provincias):
  - Valor local vs. Media provincia vs. Media comunidad vs. Media nacional
  - Indicadores: ±% vs cada nivel
- **Enlace Wikipedia**: Botón que abre `https://es.wikipedia.org/wiki/{localidad}`

---

## 4. Queries SQL

### Query Principal de Búsqueda
```sql
SELECT 
    l.id,
    l.nombre AS localidad,
    p.nombre_provincia AS provincia,
    c.nombre_comunidad AS comunidad,
    cc.puntuacion,
    cc.categoria,
    v.precio_alquiler,
    g.gasto_mensual AS gasto_alimentacion,
    h.num_hospitales_total > 0 AS tiene_hospital,
    tu.tiene_metro OR tu.tiene_autobus_municipal OR tu.tiene_tranvia AS tiene_transporte_urbano,
    cu.num_salas_cine > 0 AS tiene_cines,
    cu.num_salas_teatro > 0 AS tiene_teatros,
    cu.num_museos > 0 AS tiene_museos,
    cc.nota_costa = 1 AS es_costa,
    cc.nota_universidad > 0 AS tiene_universidad
FROM localidades l
LEFT JOIN calidad_ciudad cc ON l.id = cc.localidad_id
LEFT JOIN vivienda v ON l.id = v.localidad_id
LEFT JOIN gastos g ON l.id = g.localidad_id AND g.codigo_gasto = '01'
LEFT JOIN hospitales h ON l.id = h.localidad_id
LEFT JOIN transporte_urbano tu ON l.id = tu.localidad_id
LEFT JOIN cultura cu ON l.id = cu.localidad_id
LEFT JOIN param_provincias p ON l.codigo_provincia = p.codigo_provincia
LEFT JOIN param_comunidades c ON p.codigo_comunidad = c.codigo_comunidad
WHERE 
    (@precio_alquiler IS NULL OR v.precio_alquiler <= @precio_alquiler)
    AND (@gasto_alimentacion IS NULL OR g.gasto_mensual <= @gasto_alimentacion)
    AND (@tiene_cines = 0 OR cu.num_salas_cine > 0)
    AND (@tiene_teatros = 0 OR cu.num_salas_teatro > 0)
    AND (@tiene_museos = 0 OR cu.num_museos > 0)
    AND (@es_costa = 0 OR cc.nota_costa = 1)
    AND (@tiene_transporte_urbano = 0 OR tu.tiene_metro = 1 OR tu.tiene_autobus_municipal = 1 OR tu.tiene_tranvia = 1)
    AND (@tiene_hospital = 0 OR h.num_hospitales_total > 0)
    AND (@tiene_universidad = 0 OR cc.nota_universidad > 0)
ORDER BY cc.puntuacion DESC NULLS LAST
```

---

## 5. Pasos de Implementación

### Fase 1: Proyecto Base
1. Crear estructura de directorios `app/`
2. Crear `requirements.txt` con dependencias
3. Crear `app/__init__.py` y `app/database.py` (conexión SQLite)
4. Crear `app/models.py` (clases de datos)

### Fase 2: Componentes UI
5. Crear `app/components/filters.py` (componente de filtros)
6. Crear `app/components/score_circle.py` (círculo de puntuación)
7. Crear `app/components/city_table.py` (tabla de resultados)
8. Crear `app/components/detail_dialog.py` (ventana de detalle)

### Fase 3: Páginas
9. Crear `app/pages/main_page.py` (página principal con filtros + tabla)
10. Crear `app/main.py` (entry point con routing)

### Fase 4: Validación
11. Crear tests básicos en `tests/test_app.py`
12. Probar la aplicación

---

## 6. Dependencias
```
nicegui>=1.4.0
plotly>=6.0.0
kaleido>=1.0.0
numpy>=1.26.0
```

## 8. Implementación Realizada

### Mapa con Plotly
- Proveedor: OpenStreetMap vía Plotly scattermapbox
- Zoom adaptativo:
  - España peninsular: 3.6
  - Canarias (lat < 36): 5.9
  - Baleares (36 <= lat <= 41, 1 <= lon <= 5): 5.9
- Centro automático según zona geográfica

### Colores Scoring
- Alta Calidad: Verde oscuro (#006400)
- Media-Alta: Verde claro (#32CD32)
- Media: Amarillo (#FFD700)
- Media-Baja: Naranja (#FF8C00)
- Baja Calidad: Rojo (#DC143C)

---

## 7. Criterios de Éxito

### Funcionalidades Completadas ✅
- [x] Filtros funcionan individualmente y combinados
- [x] Tabla muestra resultados ordenados por puntuación
- [x] Círculo muestra color correcto según categoría
- [x] Puntuación transformada correctamente (1-100)
- [x] Detalle abre al pulsar localidad
- [x] Datos comparativos visibles cuando existen
- [x] Enlace Wikipedia funcional
- [x] Aplicación inicia sin errores
- [x] Mapa con Plotly/OpenStreetMap integrado
- [x] Zoom adaptativo por zona geográfica
- [x] Marcador mapa: círculo azul con tooltip personalizado
- [x] Diálogo detalle: cabecera fija + cuerpo scroll + pie fijo
- [x] Cajas Paro, Renta y Seguridad con colores comparativos
- [x] Docker configurado para Dockploy

### Completadas ✅
- [x] Mejorar UI de filtros del menú lateral (izquierda)
- [x] Mejorar cabecera de la aplicación
- [x] Mejorar diálogos detalle (header/footer fijos, scroll, 90vh)
- [x] Actualizar badges transporte (todos estáticos, añadir FEVE)

---

## 8. Estado Actual del Proyecto

**Completado**: 100% de funcionalidades principales
- ✅ Core de la aplicación (filtros, tabla, detalle, mapa)
- ✅ UI del diálogo de detalle (completa)
- ✅ Configuración Docker para producción
- ✅ UI página principal (filtros y cabecera mejorados)

**Todas las tareas completadas** ✅
