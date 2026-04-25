# app/pages/main_page.py - Página principal
"""
Página principal con filtros y tabla de resultados.
"""

from nicegui import ui
from app.database import buscar_ciudades
from app.components.filters import FiltrosComponent
from app.components.city_table import CityTableComponent
from app.components.detail_dialog import DetailDialog


class MainPage:
    """Página principal de la aplicación."""

    def __init__(self):
        self.filtros: FiltrosComponent = None
        self.tabla: CityTableComponent = None
        self.dialogo_detalle: DetailDialog = None
        self._resultados_label: ui.label = None
        self.localidad_origen: dict | None = None

    def on_row_click(self, localidad_id: int):
        """Handler para click en fila de ciudad. Abre el diálogo de detalle."""
        self.dialogo_detalle.show(localidad_id)

    def on_filter_change(self):
        """Handler para cambio de filtros."""
        filtro = self.filtros.get_filtro()
        ciudades = buscar_ciudades(filtro)
        self.tabla.update_data(ciudades)
        self._resultados_label.text = f"{len(ciudades)} ciudades encontradas"

    def build(self):
        """Construye la página."""
        # Crear diálogo de detalle primero
        self.dialogo_detalle = DetailDialog()
        self.dialogo_detalle.build()

        # Header fijo usando ui.header
        with ui.header().classes("bg-primary text-white").props("elevated"):
            with ui.row().classes("items-center gap-2 w-full"):
                ui.icon("location_city", size="sm").classes("text-white")
                ui.label("Calidad de Ciudades").classes("text-h6 font-bold")
            with ui.row().classes("w-full"):
                ui.label("Buscador de ciudades españolas por calidad de vida").classes(
                    "text-body2"
                )

# Contenedor principal con padding para el header fijo
        with ui.column().classes("w-full p-4 gap-4"):
            # Contenedor responsivo: row en PC, column en móvil
            with ui.row().classes("w-full gap-6 responsive-container"):
                # Panel de filtros (izquierda en PC, arriba en móvil)
                with ui.column().classes("w-80 filters-panel"):
                    self.filtros = FiltrosComponent(on_filter_change=self.on_filter_change)
                    self.filtros.build()

                # Panel de resultados (derecha en PC, abajo en móvil)
                with ui.column().classes("flex-grow results-panel gap-4"):
                    self._resultados_label = ui.label("0 ciudades encontradas").classes(
                        "text-body2 text-grey"
                    )
                    self.tabla = CityTableComponent(on_row_click=self.on_row_click)
                    self.tabla.build()

        # Cargar datos iniciales
        self.on_filter_change()

        # Pasar getter de localidad origen al diálogo de detalle para cálculo de distancias
        self.dialogo_detalle.set_origen_getter(lambda: self.filtros.localidad_fijada)
