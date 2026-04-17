# Visualization

Quick reference for charts and visualization elements in NiceGUI.

## Plotly Charts

### ui.chart(figure)

Plotly chart integration.

```python
import plotly.graph_objects as go

# Basic scatter
fig = go.Figure(data=[
    go.Scatter(x=[1, 2, 3], y=[1, 2, 3], mode='lines+markers')
])
ui.chart(fig)

# Bar chart
fig = go.Figure(data=[
    go.Bar(x=['A', 'B', 'C'], y=[10, 20, 15])
])
ui.chart(fig)

# Pie chart
fig = go.Figure(data=[
    go.Pie(labels=['A', 'B', 'C'], values=[30, 50, 20])
])
ui.chart(fig)
```

### Dictionary Interface (Efficient for large data)

```python
ui.chart({
    'data': [
        {'type': 'scatter', 'x': [1, 2, 3], 'y': [1, 2, 3]},
        {'type': 'scatter', 'x': [1, 2, 3], 'y': [1.4, 1.8, 3.8], 'line': {'dash': 'dot'}}
    ],
    'layout': {
        'margin': {'l': 15, 'r': 0, 't': 0, 'b': 15},
        'plot_bgcolor': '#E5ECF6'
    }
})
```

## ECharts

### ui.echart()

Apache ECharts integration.

```python
ui.echart({
    'xAxis': {'type': 'category', 'data': ['Mon', 'Tue', 'Wed']},
    'yAxis': {'type': 'value'},
    'series': [{'data': [120, 200, 150], 'type': 'line'}]
})
```

## AG Grid

### ui.aggrid()

Advanced data grid.

```python
ui.aggrid({
    'columnDefs': [
        {'field': 'make', 'checkboxSelection': True},
        {'field': 'model'},
        {'field': 'price', 'valueFormatter': "params.value.toLocaleString()"}
    ],
    'rowData': [
        {'make': 'Toyota', 'model': 'Celica', 'price': 35000},
        {'make': 'Ford', 'model': 'Mondeo', 'price': 32000}
    ]
})
```

## Media Elements

### ui.image(source)

Image display.

```python
ui.image('https://example.com/image.jpg')
ui.image('/static/image.png')

# With caption
ui.image('https://picsum.photos/id/30/270/180').props('caption="Landscape"')
```

### ui.video(source)

Video player.

```python
ui.video('https://example.com/video.mp4')
ui.video('/static/video.mp4').props('controls')
```

### ui.audio(source)

Audio player.

```python
ui.audio('/static/sound.mp3')

# With controls
a = ui.audio('sound.mp3')
a.controls()
```

### ui.youtube(video_id)

YouTube embed.

```python
ui.youtube('dQw4w9WgXcQ')
```

### ui.video_source()

Video source element.

```python
with ui.video():
    ui.video_source(src='/video.mp4', type='video/mp4')
```

## Progress Indicators

### ui.progress(value=None, max=100)

Progress bar.

```python
progress = ui.progress(value=50, max=100)
progress.set_value(75)
```

### ui.linear_progress(value=None, max=100)

Linear progress bar.

```python
ui.linear_progress(value=30, max=100).props('reverse color=positive')
```

### ui.circular_progress(value=None, max=100)

Circular progress.

```python
ui.circular_progress(value=60, max=100).props('size=50px')
```

### ui.spinner(size='lg', color=None)

Loading spinner.

```python
ui.spinner(size='xl', color='red')
ui.spinner().props('size=3rem')
```

## Color & Style

### ui.colorswatch(colors=None)

Color swatch display.

```python
swatch = ui.colorswatch(colors=['red', 'green', 'blue'])
```

### ui.color_picker(label='', value=None)

Color picker (also in Inputs).

```python
color = ui.color_picker(label='Select color')
```

## Interactive Maps

### ui.leaflet()

Map display (requires leaflet library).

```python
ui.leaflet(center=(51.505, -0.09), zoom=13)
```

### ui.map()

Simple map with markers.

```python
ui.map(center=(51.505, -0.09), zoom=13, markers=[
    {'lat': 51.505, 'lng': -0.09, 'popup': 'Marker 1'}
])
```

## Common Properties

```python
# Chart sizing
ui.chart().props('height=400px')

# Image sizing
ui.image().classes('w-64')
ui.image().props('width=300')

# Spinner variants
ui.spinner(size='sm')
ui.spinner(size='md')
ui.spinner(size='lg')
ui.spinner(size='xl')

# Colors
ui.spinner().props('color=primary')
ui.spinner().props('color=negative')
ui.spinner().props('color=positive')
```