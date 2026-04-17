# Text Elements

> **Relacionado**: Ver [inputs.md](./inputs.md) para formularios y campos de entrada

Quick reference for text display elements in NiceGUI.

## ui.label(text='')

Simple text display.

```python
ui.label('Hello World')
ui.label(f'Value: {value}')  # f-string support
ui.label().bind_text_from(source, 'property')  # Reactive
```

## ui.html(html_string)

Raw HTML rendering.

```python
ui.html('<b>Bold</b> <span style="color:red">Red</span>')
ui.html('<a href="https://example.com">Link</a>')
```

## ui.markdown(markdown_string)

Markdown rendering with full syntax support.

```python
ui.markdown('''
# Heading 1
## Heading 2

**Bold** and *italic*

- List item 1
- List item 2

```python
code block
```

[Link](https://example.com)
''')
```

## ui.code(content, language=None)

Code block display with syntax highlighting.

```python
ui.code('print("hello")', language='python')
ui.code('const x = 1;', language='javascript')
```

## ui.separator()

Horizontal divider line.

```python
ui.separator()
ui.separator().props('q-my-md')
```

## ui.text(text='')

Plain text without formatting (alias for label).

```python
ui.text('Plain text')
```

## Properties & Methods

- `.text` - Get/set text content
- `.bind_text_from(obj, attr)` - Reactive binding
- `.bind_text(obj, attr)` - Two-way binding
- `.classes()` - Add CSS classes
- `.style()` - Add inline styles
- `.props()` - Add Quasar props