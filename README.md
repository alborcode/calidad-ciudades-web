# Calidad Ciudades Web 🏙️

Aplicación web interactiva para explorar y comparar ciudades españolas según su calidad de vida. Desarrollada con **NiceGUI** (Python) y **Plotly** para visualización de mapas.

![Estado](https://img.shields.io/badge/estado-completado-success)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![NiceGUI](https://img.shields.io/badge/NiceGUI-3.10.0-green)

---

## 📋 Índice

- [Características](#-características)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Filtros de Búsqueda](#-filtros-de-búsqueda)
- [Ventana de Detalle](#-ventana-de-detalle)
- [Sistema de Puntuación](#-sistema-de-puntuación)
- [Mapa Interactivo](#-mapa-interactivo)
- [Docker](#-docker)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías](#-tecnologías)

---

## ✨ Características

- 🔍 **Búsqueda avanzada** con múltiples filtros combinables
- 📊 **Puntuación visual** con círculos de colores según calidad
- 🗺️ **Mapa interactivo** con OpenStreetMap y Plotly
- 📱 **Diseño responsivo** para PC, tablet y móvil
- 🎨 **UI moderna** con componentes reutilizables
- 🚀 **Docker ready** para despliegue en producción

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.14
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/alborcode/calidad-ciudades-web.git
cd calidad-ciudades-web
```

2. **Crear entorno virtual**:
```bash
python -m venv .venv
```

3. **Activar entorno virtual**:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

4. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

5. **Verificar instalación**:
```bash
.venv/Scripts/python.exe -c "from app.database import buscar_ciudades; print('✅ Instalación correcta')"
```

### Desarrollo Local (Opcional)

Si necesitas cambiar la configuración (puerto, host):

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Crear archivo .env (opcional)
echo PORT=9000 > .env
echo HOST=127.0.0.1 >> .env
```

**Ver guía completa**: [DESARROLLO.md](DESARROLLO.md)

---

## 💻 Uso

### Ejecutar la Aplicación

```bash
.venv/Scripts/python.exe -m app.main
```

La aplicación se abrirá automáticamente en:
```
http://localhost:8080
```

**Configuración opcional**: La aplicación usa valores por defecto (host='0.0.0.0', port=8080). Para cambiar la configuración, ver [DESARROLLO.md](DESARROLLO.md).

### Navegación Básica

1. **Página Principal**: Muestra filtros (izquierda) y resultados (derecha)
2. **Filtrar**: Usa los filtros para refinar la búsqueda
3. **Ver Detalle**: Haz click en "Ver detalle" o en la fila de una ciudad
4. **Explorar**: Navega por las diferentes secciones del detalle

---

## 🔍 Filtros de Búsqueda

La aplicación incluye **8 filtros** que pueden combinarse para refinar la búsqueda:

### Filtros Numéricos

| Filtro | Tipo | Descripción | Ejemplo |
|--------|------|-------------|---------|
| **Precio alquiler máximo** | `ui.number` | Filtra ciudades con alquiler ≤ valor especificado | `800` €/mes |

**Comportamiento**:
- Si se deja vacío: muestra todas las ciudades sin importar el precio
- Si se especifica un valor: solo muestra ciudades con alquiler ≤ ese valor
- Valores válidos: números positivos (mínimo 0, incrementos de 10)

### Filtros Booleanos (Checkboxes)

Todos los filtros booleanos funcionan con lógica **AND**:

| Filtro | Condición SQL | Descripción |
|--------|---------------|-------------|
| **Cines** ☑️ | `cultura.num_salas_cine > 0` | Ciudades con al menos 1 sala de cine |
| **Teatros** ☑️ | `cultura.num_salas_teatro > 0` | Ciudades con al menos 1 sala de teatro |
| **Museos** ☑️ | `cultura.num_museos > 0` | Ciudades con al menos 1 museo |
| **Es de costa** ☑️ | `calidad_ciudad.nota_costa = 1` | Ciudades costeras |
| **Transporte urbano** ☑️ | `tiene_metro OR tiene_autobus_municipal OR tiene_tranvia` | Ciudades con transporte público urbano |
| **Hospital** ☑️ | `sanidad.num_hospitales_total > 0` | Ciudades con al menos 1 hospital |
| **Universidad** ☑️ | `calidad_ciudad.nota_universidad > 0` | Ciudades con universidad |

### Filtro Especial: Localidad Origen

| Filtro | Tipo | Descripción |
|--------|------|-------------|
| **Localidad Origen** | Autocomplete | Establece una ciudad como referencia para calcular distancias |

**Funcionamiento**:
1. Escribe el nombre de una ciudad (mínimo 2 caracteres)
2. Selecciona de la lista de sugerencias
3. La localidad queda fijada como "origen"
4. En el detalle de cada ciudad se muestra la **distancia en km** a la localidad origen

**Ejemplo**:
```
Input: "Madrid"
→ Seleccionar "Madrid, Madrid"
→ Badge permanente: "Origen: Madrid"
→ En detalle de "Toledo": "Distancia a localidad origen: 71 km"
```

### Botones de Acción

| Botón | Acción |
|-------|--------|
| **Limpiar filtros** | Resetea todos los filtros a su estado inicial |
| **Limpiar Localidad** | Elimina la localidad origen fijada |

---

## 🏙️ Ventana de Detalle

Al hacer click en una ciudad, se abre un **diálogo modal** con información detallada organizada en secciones:

### Estructura del Diálogo

```
┌─────────────────────────────────────┐
│  CABECERA (fija)                   │
│  - Nombre, Provincia, CCAA         │
│  - Botón Wikipedia                 │
├─────────────────────────────────────┤
│  CUERPO (scroll)                   │
│  - Puntuación                      │
│  - Datos Generales                 │
│  - Ubicación (mapa)                │
│  - Clima                           │
│  - Administración                  │
│  - Vivienda                        │
│  - Transporte                      │
│  - Sanidad                         │
│  - Cultura                         │
│  - Educación                       │
│  - Paro                            │
│  - Renta                           │
│  - Seguridad                       │
├─────────────────────────────────────┤
│  PIE (fijo)                        │
│  - Botón "Cerrar"                  │
└─────────────────────────────────────┘
```

**Altura máxima**: 85vh (90% de la altura de la ventana)

### Secciones Detalladas

#### 1. Puntuación de Calidad
- **Círculo SVG** con nota 1-100
- **Color** según categoría (ver tabla más abajo)
- **Leyenda** de colores debajo del círculo

#### 2. Datos Generales
| Campo | Formato | Descripción |
|-------|---------|-------------|
| Población | `123.456` | Número de habitantes con separador de miles |
| Latitud | `40.4168` | Coordenada geográfica (4 decimales) |
| Longitud | `-3.7038` | Coordenada geográfica (4 decimales) |
| Altitud | `650 m` | Altura sobre el nivel del mar |

#### 3. Ubicación (Mapa)
- **Mapa interactivo** OpenStreetMap + Plotly
- **Marcador**: Círculo azul en la ubicación de la ciudad
- **Zoom adaptativo**:
  - **Canarias**: zoom 5.9, centro (28.5, -15.5)
  - **Baleares**: zoom 5.9, centro (39.5, 3)
  - **Península**: zoom 3.6, centro (40.5, -3.7)
- **Tooltip**: Muestra Nombre, Provincia, Población al pasar el ratón

#### 4. Clima ☀️
Comparativa con medias nacionales:

| Indicador | Color | Condición |
|-----------|-------|-----------|
| Temperatura > +10% | 🔴 Rojo | Más de 10% más cálido |
| Temperatura > +5% | 🟠 Naranja | 5-10% más cálido |
| Temperatura < -10% | 🔵 Azul marino | Más de 10% más frío |
| Temperatura < -5% | 🔵 Azul celeste | 5-10% más frío |
| Precipitaciones > +25% | 🔵 Azul | 25% más lluvias |
| Precipitaciones > +15% | 🔵 Cyan | 15-25% más lluvias |
| Precipitaciones < -25% | 🔴 Rojo | 25% menos lluvias |
| Precipitaciones < -15% | 🟠 Naranja | 15-25% menos lluvias |
| Viento > +15% | 🔴 Rojo | Más de 15% más viento |
| Viento > media | 🟠 Naranja | Más viento que media |

#### 5. Administración 🏛️
Muestra badges con organismos presentes:
- AEAT, Hacienda, Seguridad Social, AEMET, CSIC, Defensa, SEPE, IMSERSO, Cultura, INE, Comercio, Educación, Justicia, Deleg. Gobierno, Sanidad, Carreteras, Marina Mercante, DGT, Policía, MUGEFU

#### 6. Vivienda 🏠
Comparativa con medias nacionales (colores según desviación):

| Indicador | Color | Condición |
|-----------|-------|-----------|
| Precio alquiler > nacional | 🔴 Rojo | Más caro |
| Precio alquiler = nacional | 🟠 Naranja | Igual |
| Precio alquiler < nacional | 🟢 Verde | Más barato |
| Superficie > nacional | 🟢 Verde | Más grande (mejor) |
| Superficie < nacional | 🔴 Rojo | Más pequeña (peor) |

**Indicadores**:
- Precio Alquiler medio (€/mes)
- Precio m² (€/m²)
- Superficie media (m²)
- % Viviendas turísticas

#### 7. Transporte 🚆
Badges clickeables para transporte urbano:

| Tipo | Color | Clickable |
|------|-------|-----------|
| Aeropuerto | 🔵 Primary | ❌ |
| AVE/Media Distancia | 🔵 Primary | ❌ |
| Regional | 🔵 Primary | ❌ |
| Cercanías | 🟠 Amber-8 | ❌ |
| Metro | 🟠 Amber-8 | ✅ Muestra líneas |
| Autobús municipal | 🟠 Amber-8 | ✅ Muestra rutas |
| Tranvía | 🟠 Amber-8 | ✅ Muestra líneas |

#### 8. Sanidad 🏥
- **Hospitales**: Número total + botón clickeable para ver lista
- **Centros de Salud**: Número total + botón clickeable para ver lista

**Ventana de hospitales**: Muestra nombre, dirección, CP, teléfono de cada hospital

#### 9. Cultura y Ocio 🎭
- **Cines**: Número de salas + botón para ver lista
- **Teatros**: Número de salas + botón para ver lista
- **Museos**: Número total + botón para ver lista

#### 10. Educación 📚
- **Bibliotecas**: Número + lista con tipo, dependencia, dirección
- **Universidades**: Número + lista con año fundación, tipo, web
- **Institutos/Colegios**: Número + lista con nombre, tipo, dirección

#### 11. Paro 💼
Comparativa con tasa nacional (5.11%):

| Indicador | Color | Condición |
|-----------|-------|-----------|
| Tasa desempleo > nacional | 🔴 Rojo | Peor que media |
| Tasa desempleo < nacional | 🟢 Verde | Mejor que media |
| Evolución trimestral < 0 | 🟢 Verde | Bajó el paro |
| Evolución trimestral > 0 | 🔴 Rojo | Subió el paro |

#### 12. Renta 💰
Comparativa con renta neta nacional (13.268€):

| Nivel | Color | Condición |
|-------|-------|-----------|
| > +5% sobre nacional | 🔴 Rojo | Renta muy alta |
| > 0% hasta +5% | 🟠 Naranja | Renta alta |
| < 0% hasta -5% | 🟢 Verde | Renta baja |
| < -5% sobre nacional | 🟢 Verde oscuro | Renta muy baja |

**Indicadores**:
- Renta bruta media (€)
- Renta neta media (€)
- Variación renta bruta (%)
- Media nacional (referencia)

#### 13. Seguridad ⚠️
Comparativa con tasas nacionales:

| Indicador | Referencia Nacional | Color |
|-----------|---------------------|-------|
| Tasa criminalidad | 40.4 | 🔴 > nacional, 🟢 < nacional |
| Tasa Robos | 1.26 | 🔴 > nacional, 🟢 < nacional |

---

## 📊 Sistema de Puntuación

### Fórmula de Transformación

La base de datos usa un rango de **-2 a 18**. La aplicación transforma a escala **1-100**:

```python
puntuacion_100 = ((score + 2) / 20) * 99 + 1
```

**Ejemplos**:
- Score -2 → 1 (mínimo)
- Score 0 → 10.9
- Score 8 → 50.5
- Score 18 → 100 (máximo)

### Categorías y Colores

| Categoría | Rango 100 | Color | Código Hex |
|-----------|-----------|-------|------------|
| **Alta** | 80-100 | Verde oscuro | `#006400` |
| **Media-Alta** | 60-79 | Verde claro | `#32CD32` |
| **Media** | 40-59 | Amarillo | `#FFD700` |
| **Media-Baja** | 20-39 | Naranja | `#FF8C00` |
| **Baja** | 1-19 | Rojo | `#DC143C` |

### Visualización

- **Círculo SVG**: Muestra la puntuación 1-100 con color de categoría
- **Badge**: Etiqueta con nombre de categoría en resultados
- **Leyenda**: 5 puntos de color con etiquetas en el diálogo

---

## 🗺️ Mapa Interactivo

### Tecnología

- **Proveedor**: OpenStreetMap
- **Librería**: Plotly `scattermapbox`
- **Renderizado**: `ui.plotly()` de NiceGUI

### Configuración por Zona

#### España Peninsular (default)
```python
map_center = dict(lat=40.5, lon=-3.7)
map_zoom = 3.6
```

#### Canarias
```python
# Se activa si latitud < 36
map_center = dict(lat=28.5, lon=-15.5)
map_zoom = 5.9
```

#### Baleares
```python
# Se activa si 36 ≤ lat ≤ 41 Y 1 ≤ lon ≤ 5
map_center = dict(lat=39.5, lon=3)
map_zoom = 5.9
```

### Elementos del Mapa

| Elemento | Configuración | Descripción |
|----------|---------------|-------------|
| **Marcador** | `symbol="circle"`, `size=10`, `color="blue"` | Círculo azul en la ciudad |
| **Texto** | `size=10`, `position="top center"` | Nombre de la ciudad sobre el marcador |
| **Tooltip** | `bgcolor="rgba(173, 216, 230, 0.9)"` | Fondo azul claro con Nombre, Provincia, Población |

### Contenedor

```css
width: 100%;
max-width: 100%;
overflow: hidden;
position: relative;
```

**Propósito**: Evitar que el mapa se salga del contenedor en pantallas pequeñas.

---

## 🐳 Docker

### Despliegue en Producción (Dockploy)

1. **Subir la base de datos al servidor**:
```bash
scp data/calidad_ciudades.db usuario@servidor:/path/to/data/
```

2. **Configurar en Dockploy**:
- **Repository URL**: `https://github.com/alborcode/calidad-ciudades-web.git`
- **Branch**: `main`
- **Volumes**: `/path/to/data:/app/data`
- **Ports**: `8080:8080`

3. **Desplegar**: Click en "Deploy" en Dockploy

### Desarrollo Local

```bash
# Build
docker build -t calidad-ciudades-web .

# Ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

**Ver guía completa**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

## 📁 Estructura del Proyecto

```
calidad-ciudades-web/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── database.py          # Conexión SQLite y queries
│   ├── models.py            # Dataclasses
│   ├── components/          # Componentes UI reutilizables
│   │   ├── __init__.py
│   │   ├── filters.py       # Filtros de búsqueda
│   │   ├── city_table.py    # Tabla de resultados
│   │   ├── score_circle.py  # Círculo de puntuación SVG
│   │   └── detail_dialog.py # Diálogo de detalle
│   ├── pages/
│   │   ├── __init__.py
│   │   └── main_page.py     # Página principal
│   └── utils/
│       ├── __init__.py
│       ├── visuals.py       # Helpers visuales
│       └── geo.py           # Funciones geográficas (haversine)
├── data/
│   └── calidad_ciudades.db  # Base de datos SQLite (427 ciudades)
├── tests/
│   └── test_app.py          # Tests unitarios
├── .venv/                   # Entorno virtual (no versionado)
├── .dockerignore            # Archivos excluidos de Docker
├── .gitignore               # Archivos ignorados por Git
├── Dockerfile               # Configuración Docker
├── docker-compose.yml       # Ejemplo desarrollo local
├── DOCKER_DEPLOYMENT.md     # Guía de despliegue
├── DESARROLLO.md            # Guía desarrollo local
├── MEMORY.md                # Estado del proyecto
├── PLAN.md                  # Planificación y tareas
├── AGENTS.md                # Contexto para agentes IA
├── RULES.md                 # Reglas del proyecto
├── README.md                # Este archivo
└── requirements.txt         # Dependencias Python
```

---

## 🛠️ Tecnologías

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.14 | Lenguaje principal |
| **SQLite** | 3.x | Base de datos embebida |
| **NiceGUI** | 3.10.0 | Framework UI web |

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Plotly** | 6.7.0 | Mapas interactivos |
| **Kaleido** | 1.2.0 | Renderizado estático de gráficos |
| **NumPy** | 2.4.4 | Cálculos numéricos |

### Infraestructura
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Docker** | 20.10+ | Contenerización |
| **Dockploy** | - | Orquestación (producción) |

---

## 📊 Base de Datos

### Tablas Principales

| Tabla | Descripción | Columnas clave |
|-------|-------------|----------------|
| `localidades` | Datos básicos de ciudades | `id`, `nombre`, `latitud`, `longitud`, `poblacion` |
| `calidad_ciudad` | Puntuación y categoría | `nota_final`, `categoria`, `nota_costa`, `nota_universidad` |
| `vivienda` | Precios de vivienda | `precio_alquiler`, `precio_m2`, `superficie_media_m2` |
| `gastos` | Gastos por categoría | `codigo_gasto`, `gasto_mensual` |
| `sanidad` | Infraestructura sanitaria | `num_hospitales_total`, `num_centros_salud` |
| `transporte_urbano` | Transporte público | `tiene_metro`, `tiene_autobus_municipal`, `tiene_tranvia` |
| `cultura` | Ocio y cultura | `num_salas_cine`, `num_salas_teatro`, `num_museos` |
| `datos_nacionales` | Medias nacionales | `tipo`, `valor` |

### Datos de Referencia

| Concepto | Valor |
|----------|-------|
| Tasa paro nacional | 5.11% |
| Tasa criminalidad nacional | 40.4 |
| Tasa robos nacional | 1.26 |
| Renta bruta media | 16.712€ |
| Renta neta media | 13.268€ |

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest tests/ -v
```

### Verificar Imports

```bash
.venv/Scripts/python.exe -c "from app.database import buscar_ciudades, CiudadFiltro"
```

---

## 📝 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

---

## 👥 Contacto

Para más información, consultar la documentación interna:
- [MEMORY.md](MEMORY.md) - Estado actual del proyecto
- [PLAN.md](PLAN.md) - Planificación y tareas pendientes
- [AGENTS.md](AGENTS.md) - Contexto técnico y reglas
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Guía de despliegue

---

**Última actualización**: 2026-04-25
