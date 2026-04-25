# Docker Deployment - Calidad Ciudades Web

## Descripción

Configuración Docker para desplegar la aplicación Calidad Ciudades Web en producción con Dockploy.

## Estructura de Archivos

```
├── Dockerfile              # Imagen de producción
├── .dockerignore           # Archivos excluidos del build
├── docker-compose.yml      # Ejemplo desarrollo local (opcional)
└── DOCKER_DEPLOYMENT.md    # Este archivo
```

## Configuración en Dockploy

### 1. Subir la Base de Datos

La base de datos **NO** está en el repositorio. Debes subirla manualmente al servidor:

```bash
# Copiar BD al servidor
scp data/calidad_ciudades.db usuario@servidor:/path/to/data/

# Copiar directorio data completo (si incluye CSV, XLS, etc.)
scp -r data/ usuario@servidor:/path/to/data/
```

### 2. Configurar en Dockploy

**Repository URL:**
```
https://github.com/alborcode/calidad-ciudades-web.git
```

**Branch:**
```
main
```

**Docker Context:**
```
.
```

**Dockerfile:**
```
Dockerfile
```

**Volumes (Importante):**
```
/path/en/servidor/data:/app/data
```

Ejemplo:
```
/home/usuario/calidad-ciudades-data:/app/data
```

**Ports:**
```
8080:8080
```

**Environment Variables:**
```
PYTHONUNBUFFERED=1
```

**Build Args:** (opcional, dejar vacío)

**Deploy Command:** (dejar por defecto)

### 3. Desplegar

1. Guardar configuración en Dockploy
2. Click en "Deploy"
3. Esperar a que el build complete (~2-3 minutos)
4. Acceder a `http://tu-servidor:8080`

## Desarrollo Local (Opcional)

Para testing local con Docker:

```bash
# Build de la imagen
docker build -t calidad-ciudades-web .

# Ejecutar con docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## Estructura del Contenedor

```
/app/
├── app/                    # Código de la aplicación
│   ├── main.py
│   ├── database.py
│   ├── components/
│   └── ...
├── data/                   # Volumen montado desde el servidor
│   ├── calidad_ciudades.db
│   ├── csv/
│   ├── xls/
│   └── ...
└── requirements.txt
```

## Consideraciones

### Base de Datos

- La BD se monta como volumen persistente
- Actualizaciones de BD: copiar nuevo archivo `.db` y reiniciar contenedor
- Backup: copiar archivo `.db` del directorio de datos

### Actualizaciones

1. Hacer push a `main`
2. Dockploy detecta cambios automáticamente
3. Redeploy automático o manual desde UI

### Logs

```bash
# Desde Dockploy UI
# O desde servidor:
docker logs calidad-ciudades-web -f
```

### Reiniciar Contenedor

```bash
# Desde Dockploy UI
# O desde servidor:
docker restart calidad-ciudades-web
```

## Troubleshooting

### Error: "Database not found"

Verificar que el volumen está montado correctamente:
```bash
docker inspect calidad-ciudades-web | grep -A 10 Mounts
```

### Error: "Port already in use"

El puerto 8080 está ocupado. Cambiar en Dockploy:
```
Host Port: 8081 (u otro disponible)
Container Port: 8080
```

### Ver estado del contenedor

```bash
docker ps | grep calidad-ciudades
docker stats calidad-ciudades-web
```

## Requisitos del Servidor

- Docker 20.10+
- Docker Compose 2.0+ (solo para desarrollo local)
- 512MB RAM mínimo (1GB recomendado)
- 1GB disco (más si se incluyen datos históricos)

## Seguridad

- ✅ Usuario no-root en contenedor (python:slim)
- ✅ Sin archivos innecesarios (`.dockerignore`)
- ✅ Volúmenes persistentes para datos
- ⚠️ Configurar firewall para puerto 8080
- ⚠️ Usar HTTPS con proxy inverso (nginx/traefik) si es necesario
