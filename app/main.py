# app/main.py - Entry point
"""
Entry point de la aplicación Calidad Ciudades Web.
"""

from nicegui import ui
from app.pages.main_page import MainPage


@ui.page("/")
def main():
    """Página principal de la aplicación."""
    page = MainPage()
    page.build()


# Entry point directo
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Calidad de Ciudades",
        reload=True,
        port=8080,
        storage_secret="calidad-ciudades-secret-2024",
    )
