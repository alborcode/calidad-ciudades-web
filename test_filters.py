#!/usr/bin/env python3
"""Script de prueba para verificar el autocompletado de localidades."""

import sys
sys.path.insert(0, '.')

from app.components.filters import FiltrosComponent
from nicegui import ui

def dummy_callback():
    print("Callback de filtros llamado")

# Crear componente
filtros = FiltrosComponent(dummy_callback)

# Construir UI
@ui.page('/test')
def test_page():
    filtros.build()
    ui.label("Prueba de autocompletado").classes("text-h4")

# Ejecutar
if __name__ == "__main__":
    ui.run(storage_secret='test', port=8081, reload=False)