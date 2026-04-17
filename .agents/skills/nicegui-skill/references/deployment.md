# Deployment & Configuration

Quick reference for deploying and configuring NiceGUI applications.

## Basic Run

### ui.run()

Start the NiceGUI server.

```python
from nicegui import ui

ui.label('Hello!')
ui.run()
# Opens at http://localhost:8080
```

## Common Configuration

### Port & Host

```python
ui.run(port=8080)
ui.run(port=8080, host='0.0.0.0')  # Accessible externally
ui.run(port=8080, host='127.0.0.1')  # Local only
```

### Development vs Production

```python
# Development (with auto-reload)
ui.run(reload=True)

# Production (no auto-reload)
ui.run(reload=False)
```

### Browser Options

```python
ui.run(show=True)      # Open browser on startup
ui.run(show=False)     # Don't open browser

ui.run(open=False)     # Alias for show
```

### Title & Favicon

```python
ui.run(title='My App')
ui.run(favicon='icon.png')  # Local file or URL
```

### Welcome Message

```python
ui.run(show_welcome_message=False)
```

## SSL/HTTPS

### Self-Signed Certificates

```python
ui.run(
    ssl_certfile='cert.pem',
    ssl_keyfile='key.pem'
)
```

### Generate Self-Signed

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

## Uvicorn Options

### Logging

```python
ui.run(uvicorn_logging_level='debug')
ui.run(uvicorn_logging_level='info')
ui.run(uvicorn_logging_level='warning')
ui.run(uvicorn_logging_level='error')
```

### Auto-Reload

```python
# Reload on file changes
ui.run(
    uvicorn_reload=True,
    uvicorn_reload_dirs=['.'],
    uvicorn_reload_includes=['*.py'],
    uvicorn_reload_excludes=['*.txt', '*.log']
)
```

### Additional Uvicorn Arguments

```python
ui.run(
    workers=4,              # Number of worker processes
    log_level='info',       # Log level
    limit_concurrency=100,  # Max concurrent connections
    limit_max_requests=1000  # Restart worker after X requests
)
```

## Storage & Sessions

### Storage Secret

```python
ui.run(storage_secret='my-secret-key')
```

Used for browser-based storage encryption.

### Session Middleware

```python
ui.run(
    session_middleware_kwargs={
        'secret_key': 'your-secret',
        'session_cookie': 'nicegui-session',
        'max_age': 3600  # seconds
    }
)
```

## Tailwind CSS

### Enable Tailwind (Experimental)

```python
ui.run(tailwind=True)
ui.run(tailwind=True, watch=['./css/*.css'])
```

## UnoCSS

### Enable UnoCSS

```python
ui.run(unocss=True)
ui.run(unocss=True, unocss_presets=['@unocss/preset-uno'])
```

## OpenAPI Documentation

### Documentation Visibility

```python
ui.run(endpoint_documentation='render')  # Show in footer
ui.run(endpoint_documentation='page')     # Separate page at /docs
ui.run(endpoint_documentation=False)      # Disable
```

## FastAPI Integration

### Standalone

```python
from fastapi import FastAPI
import nicegui

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Hello from FastAPI'}

nicegui.ui.run_with(app)
```

### With Custom Routes

```python
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import nicegui

app = FastAPI()

@app.get('/api/health')
def health():
    return {'status': 'healthy'}

@app.get('/api/data')
def get_data():
    return {'data': [1, 2, 3]}

nicegui.ui.run_with(app)

# NiceGUI pages
@nicegui.ui.page('/')
def home():
    ui.label('Hello from NiceGUI!')
```

### Using app.context

```python
app = FastAPI()

# NiceGUI routes
@nicegui.ui.page('/')
def main_page():
    ui.label('Main Page')

# Run
nicegui.ui.run_with(app)

# Or using the decorator
@nicegui.ui.page('/special')
def special_page():
    ui.label('Special Page')
```

## Flask Integration

### Using `run_with_app`

```python
from flask import Flask
import nicegui

flask_app = Flask(__name__)

@flask_app.route('/api/hello')
def hello():
    return {'message': 'Hello from Flask'}

nicegui.ui.run_with_app(flask_app)
```

## Reverse Proxy

### NGINX Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### NGINX with SSL

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Traefik Configuration

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.nicegui.rule=Host(`example.com`)"
  - "traefik.http.routers.nicegui.entrypoints=websecure"
  - "traefik.http.routers.nicegui.tls.certresolver=letsencrypt"
  - "traefik.http.services.nicegui.loadbalancer.server.port=8080"
```

## Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py", "--port=8080"]
```

### docker-compose.yml

```yaml
services:
  nicegui:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
    restart: unless-stopped
```

## Production Checklist

- [ ] `ui.run(reload=False)`
- [ ] Set specific port
- [ ] Configure SSL certificates
- [ ] Set storage secret
- [ ] Disable welcome message in production
- [ ] Use reverse proxy for SSL termination
- [ ] Set up logging
- [ ] Configure worker processes
- [ ] Set up health check endpoint

## Environment Variables

```python
# Via ui.run
ui.run(
    port=int(os.getenv('PORT', 8080)),
    reload=os.getenv('ENV') == 'development'
)
```