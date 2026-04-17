# app/components/filters.py - Componente de filtros
"""
Componente de filtros para búsqueda de ciudades.
Proporciona UI para todos los filtros de búsqueda.
"""

from nicegui import ui
from app.database import CiudadFiltro


class FiltrosComponent:
    """Componente de filtros de búsqueda."""

    def __init__(self, on_filter_change: callable):
        """
        Args:
            on_filter_change: Callback llamado cuando cambian los filtros
        """
        self.on_filter_change = on_filter_change
        self.precio_alquiler: ui.Number = None
        self.gasto_alimentacion: ui.Number = None
        self.tiene_cines: ui.Checkbox = None
        self.tiene_teatros: ui.Checkbox = None
        self.tiene_museos: ui.Checkbox = None
        self.es_costa: ui.Checkbox = None
        self.tiene_transporte: ui.Checkbox = None
        self.tiene_hospital: ui.Checkbox = None
        self.tiene_universidad: ui.Checkbox = None
        self._container: ui.Column = None

    def get_filtro(self) -> CiudadFiltro:
        """Obtiene el filtro actual basado en los valores del UI."""
        precio = self.precio_alquiler.value
        gasto = self.gasto_alimentacion.value

        return CiudadFiltro(
            precio_alquiler_max=precio if precio and precio > 0 else None,
            gasto_alimentacion_max=gasto if gasto and gasto > 0 else None,
            tiene_cines=self.tiene_cines.value,
            tiene_teatros=self.tiene_teatros.value,
            tiene_museos=self.tiene_museos.value,
            es_costa=self.es_costa.value,
            tiene_transporte_urbano=self.tiene_transporte.value,
            tiene_hospital=self.tiene_hospital.value,
            tiene_universidad=self.tiene_universidad.value,
        )

    def _notify_change(self):
        """Notifica al callback que los filtros cambiaron."""
        if self.on_filter_change:
            self.on_filter_change()

    def clear_filters(self):
        """Limpia todos los filtros."""
        self.precio_alquiler.set_value(None)
        self.gasto_alimentacion.set_value(None)
        self.tiene_cines.set_value(False)
        self.tiene_teatros.set_value(False)
        self.tiene_museos.set_value(False)
        self.es_costa.set_value(False)
        self.tiene_transporte.set_value(False)
        self.tiene_hospital.set_value(False)
        self.tiene_universidad.set_value(False)
        self._notify_change()

    def build(self) -> ui.Column:
        """Construye y retorna el componente UI."""
        with ui.column().classes("gap-4") as self._container:
            # Título
            ui.label("Filtros de Búsqueda").classes("text-h6 font-bold")

            # Fila 1: Precios
            with ui.row().classes("gap-4 items-end"):
                self.precio_alquiler = ui.number(
                    label="Precio alquiler máximo (€/mes)",
                    placeholder="Ej: 800",
                    min=0,
                    step=10,
                ).on_value_change(lambda: self._notify_change())

                self.gasto_alimentacion = ui.number(
                    label="Gasto alimentación máx. (€/mes)",
                    placeholder="Ej: 300",
                    min=0,
                    step=10,
                ).on_value_change(lambda: self._notify_change())

            # Separador
            ui.separator()

            # Título servicios
            ui.label("Servicios requeridos").classes("text-subtitle1 font-medium")

            # Fila 2: Cultura
            with ui.row().classes("gap-6"):
                self.tiene_cines = ui.checkbox("Cines").on_value_change(
                    lambda: self._notify_change()
                )
                self.tiene_teatros = ui.checkbox("Teatros").on_value_change(
                    lambda: self._notify_change()
                )
                self.tiene_museos = ui.checkbox("Museos").on_value_change(
                    lambda: self._notify_change()
                )

            # Fila 3: Otros servicios
            with ui.row().classes("gap-6"):
                self.tiene_transporte = ui.checkbox(
                    "Transporte urbano"
                ).on_value_change(lambda: self._notify_change())
                self.tiene_hospital = ui.checkbox("Hospital").on_value_change(
                    lambda: self._notify_change()
                )
                self.tiene_universidad = ui.checkbox("Universidad").on_value_change(
                    lambda: self._notify_change()
                )

            # Fila 4: Localización
            with ui.row().classes("gap-6"):
                self.es_costa = ui.checkbox("Es de costa").on_value_change(
                    lambda: self._notify_change()
                )

            # Botón limpiar
            ui.button(
                "Limpiar filtros", on_click=self.clear_filters, icon="filter_alt_off"
            ).props("flat color=grey")

        return self._container
