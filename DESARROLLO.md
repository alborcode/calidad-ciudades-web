# Desarrollo Local - Calidad Ciudades Web

## Instalación

### 1. Instalar dependencias de producción

```bash
pip install -r requirements.txt
```

### 2. Instalar dependencias de desarrollo (opcional)

```bash
pip install -r requirements-dev.txt
```

Esto incluye `python-dotenv` para cargar variables de entorno desde un archivo `.env`.

## Ejecutar la App

```bash
.venv/Scripts/python.exe -m app.main
```

Abre: http://localhost:8080

## Variables de Entorno (Opcional)

Si necesitas cambiar la configuración por defecto:

1. Crea un archivo `.env` en la raíz del proyecto:
   ```
   PORT=9000
   HOST=127.0.0.1
   ```

2. Asegúrate de tener `python-dotenv` instalado:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Ejecuta la app normalmente - cargará las variables del `.env` automáticamente.

**Nota:** En producción (Docker) no hace falta configurar nada, usa los valores por defecto.
