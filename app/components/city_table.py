# app/components/city_table.py - Tabla de ciudades
"""
Componente de tabla para mostrar resultados de búsqueda de ciudades.
Incluye círculo de puntuación y click para ver detalle.
"""

from nicegui import ui
from typing import Callable
from app.database import (
    CiudadResultado,
    calcular_puntuacion_100,
    get_categoria_from_score,
)
from app.components.score_circle import crear_circulo_puntuacion, crear_badge_categoria


class CityTableComponent:
    """Componente de tabla de ciudades con resultados filtrados."""

    def __init__(self, on_row_click: Callable[[int], None]):
        """
        Args:
            on_row_click: Callback llamado con ID de localidad al hacer click
        """
        self.on_row_click = on_row_click
        self._table: ui.table = None
        self._rows_container: ui.column = None
        self._container: ui.column = None

    def update_data(self, ciudades: list[CiudadResultado]):
        """
        Actualiza la tabla con nuevos datos.

        Args:
            ciudades: Lista de resultados de búsqueda
        """
        # Limpiar contenedor
        self._rows_container.clear()

        if not ciudades:
            with self._rows_container:
                ui.label("No se encontraron ciudades con los filtros seleccionados.")
                ui.label("Prueba a modificar los filtros o ampliar la búsqueda.")
            return

        # Agregar resultados
        with self._rows_container:
            for ciudad in ciudades:
                self._crear_row(ciudad)

    def _crear_row(self, ciudad: CiudadResultado):
        """Crea una fila de resultado."""
        # Calcular categoría basada en puntuación 100 (nueva escala 28=100)
        puntuacion_100 = calcular_puntuacion_100(ciudad.puntuacion)
        categoria = get_categoria_from_score(puntuacion_100)

        with ui.card().tight().classes("w-full mb-2 p-3"):
            with ui.row().classes("w-full items-center gap-4"):
                # Círculo de puntuación
                crear_circulo_puntuacion(ciudad.puntuacion, categoria, tamano="50px")

                # Info de la ciudad
                with ui.column().classes("flex-grow"):
                    ui.label(ciudad.localidad).classes("text-h6 font-medium")
                    with ui.row().classes("gap-2 items-center"):
                        ui.label(ciudad.provincia).classes("text-body2 text-grey-7")
                        ui.label("•").classes("text-grey-5")
                        ui.label(ciudad.comunidad).classes("text-body2 text-grey-7")

                # Badge de categoría (calculada dinámicamente)
                crear_badge_categoria(categoria)

                # Botón ver detalle
                ui.button(
                    "Ver detalle",
                    on_click=lambda e, cid=ciudad.id: self.on_row_click(cid),
                    icon="info",
                ).props("flat color=primary")

    def build(self) -> ui.column:
        """Construye y retorna el componente UI."""
        with ui.column().classes("w-full gap-4") as self._container:
            # Header con contador
            with ui.row().classes("w-full justify-between items-center"):
                ui.label("Resultados").classes("text-h6 font-bold")
                ui.label("").classes(
                    "text-body2 text-grey"
                )  # Placeholder para contador

            # Contenedor de filas (se actualiza dinámicamente)
            with ui.column().classes("w-full gap-2") as self._rows_container:
                ui.label("Use los filtros para buscar ciudades.")
                ui.label("Se mostrarán aquí los resultados.")

        self._container = self._container
        return self._container
