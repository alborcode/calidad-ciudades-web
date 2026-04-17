# API & Integration

Quick reference for API endpoints, external integrations, and combining NiceGUI with other frameworks.

## FastAPI Integration

### Basic Integration

```python
from fastapi import FastAPI
import nicegui

app = FastAPI()

@app.get('/api/health')
def health():
    return {'status': 'healthy'}

@app.get('/api/data')
def get_data():
    return {'data': [1, 2, 3]}

# Add NiceGUI
nicegui.ui.run_with(app)
```

### Using the Decorator

```python
import nicegui
from fastapi import FastAPI

app = FastAPI()
nicegui.ui.run_with(app)

@nicegui.ui.page('/gui')
def gui_page():
    ui.label('Hello from NiceGUI!')

# FastAPI routes still work
@app.get('/api/hello')
def api_hello():
    return {'message': 'hello'}
```

### With Custom Root

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import nicegui

app = FastAPI()

@app.get('/')
def root():
    return RedirectResponse('/gui')

nicegui.ui.run_with(app)

@nicegui.ui.page('/gui')
def gui():
    ui.label('NiceGUI Page')
```

## Flask Integration

### Basic Setup

```python
from flask import Flask
import nicegui

flask_app = Flask(__name__)

@flask_app.route('/api/data')
def api_data():
    return {'result': 'ok'}

nicegui.ui.run_with_app(flask_app)
```

### With Blueprints

```python
from flask import Flask, Blueprint
import nicegui

app = Flask(__name__)
api = Blueprint('api', __name__)

@api.route('/health')
def health():
    return {'status': 'ok'}

app.register_blueprint(api)
nicegui.ui.run_with_app(app)
```

## OpenAPI Documentation

### Enable OpenAPI

```python
# Show in UI footer
ui.run(endpoint_documentation='render')

# Separate page at /docs
ui.run(endpoint_documentation='page')

# Disable
ui.run(endpoint_documentation=False)
```

### Custom API Routes

```python
from fastapi import APIRouter

router = APIRouter()

@router.get('/custom')
def custom():
    return {'custom': 'endpoint'}

# Include in OpenAPI
app.include_router(router, prefix='/api')
```

## Database Integration

### SQLite Example

```python
import sqlite3

conn = sqlite3.connect('data.db')

@ui.page('/users')
def users_page():
    cursor = conn.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    for row in rows:
        ui.label(row[1])

@ui.page('/add_user')
def add_user(name):
    conn.execute('INSERT INTO users (name) VALUES (?)', (name,))
    conn.commit()
```

### With SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)

@ui.page('/products')
def products():
    session = Session()
    products = session.query(Product).all()
    for p in products:
        ui.label(p.name)
    session.close()
```

## External APIs

### HTTP Client (httpx)

```python
import httpx

async def fetch_api():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com/data')
        return response.json()

@ui.page('/external')
async def external_page():
    data = await fetch_api()
    ui.label(str(data))
```

### GraphQL

```python
import httpx

async def query_graphql(query, variables=None):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.example.com/graphql',
            json={'query': query, 'variables': variables}
        )
        return response.json()

@ui.page('/graphql')
async def graphql_page():
    result = await query_graphql('{ users { name } }')
    for user in result['data']['users']:
        ui.label(user['name'])
```

### REST API Pattern

```python
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    async def get(self, endpoint):
        async with httpx.AsyncClient() as client:
            return await client.get(f'{self.base_url}{endpoint}')
    
    async def post(self, endpoint, data):
        async with httpx.AsyncClient() as client:
            return await client.post(f'{self.base_url}{endpoint}', json=data)

api = APIClient('https://api.example.com')
```

## WebSocket Communication

### Client to Server

```python
# Automatic - events go via WebSocket
button.on('click', handler)  # Handler runs on server
```

### Server to Client

```python
# Broadcast to all clients
async def notify_all(message):
    for client in ui.context.clients:
        await client.send({'type': 'update', 'data': message})

# Or from background task
async def periodic_update():
    while True:
        await asyncio.sleep(5)
        await notify_all({'time': datetime.now()})

background_tasks.create(periodic_update())
```

### Custom WebSocket

```python
@nicegui.ui.page('/ws')
async def ws_page():
    ws = ui.context.client.ws
    
    # Send to client
    await ws.send({'message': 'hello'})
    
    # Receive from client
    async for msg in ws:
        handle_message(msg)
```

## UI Component Libraries

### Loading Quasar Components

```python
# Use any Quasar component via ui.element
ui.element('q-btn').props('color=primary label=Click')
ui.element('q-card')
ui.element('q-dialog')
```

### Custom Vue Components

```python
# Register custom component
ui.add_library({
    'name': 'my-component',
    'version': '1.0.0',
    'files': ['my-component.umd.js']
})

# Use
ui.element('my-component')
```

## Environment Variables

### Configuration

```python
import os

ui.run(
    port=int(os.getenv('PORT', 8080)),
    reload=os.getenv('ENV') == 'development',
    title=os.getenv('APP_TITLE', 'NiceGUI App')
)
```

### .env Files

```python
# Use python-dotenv
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('API_KEY')
```

## Logging

### Application Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@ui.page('/')
def index():
    logger.info('Page visited')
    ui.label('Hello')
```

### Uvicorn Logs

```python
ui.run(
    log_level='info',
    uvicorn_logging_level='info'
)
```

## Error Handling

### Custom Error Pages

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={'error': 'Not found'}
    )

nicegui.ui.run_with(app)
```

### Global Exception Handler

```python
@ui.page('/error_test')
def error_page():
    try:
        # risky operation
        pass
    except Exception as e:
        ui.notify(f'Error: {e}', type='negative')
        logger.exception('Error in page')
```

## Performance

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(key):
    # Expensive operation
    return compute(key)

# In page
data = get_cached_data(param)
```

### Lazy Loading

```python
# Load heavy components on demand
@ui.refreshable
def heavy_component():
    # Only renders when called
    pass
```

## Metrics & Monitoring

### Simple Metrics

```python
import time

requests = {'count': 0}

@ui.page('/')
def index():
    requests['count'] += 1
    ui.label(f'Requests: {requests["count"]}')
```

### Health Check

```python
@app.get('/health')
def health():
    return {
        'status': 'healthy',
        'requests': requests['count']
    }
```