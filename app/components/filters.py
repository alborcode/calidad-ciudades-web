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
        self.tiene_cines: ui.Checkbox = None
        self.tiene_teatros: ui.Checkbox = None
        self.tiene_museos: ui.Checkbox = None
        self.es_costa: ui.Checkbox = None
        self.tiene_transporte: ui.Checkbox = None
        self.tiene_hospital: ui.Checkbox = None
        self.tiene_universidad: ui.Checkbox = None
        self._container: ui.Column = None
        # Localidad origen (para cálculo de distancias)
        self.localidad_input = None
        self._localidades_suggestions: list[dict] = []
        self._localidades_container: ui.Column | None = None
        self.localidad_fijada: dict | None = None
        # Flag para suprimir el handler on_value_change cuando rellenamos el input programáticamente
        self._suppress_input_change = False
        self.localidad_fijada: dict | None = None
        self._badge_container: ui.Row | None = None

    def get_filtro(self) -> CiudadFiltro:
        """Obtiene el filtro actual basado en los valores del UI."""
        precio = self.precio_alquiler.value

        return CiudadFiltro(
            precio_alquiler_max=precio if precio and precio > 0 else None,
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

    def _on_localidad_input_change(self, value: str):
        """Callback cuando cambia el texto del input de localidad. Recupera sugerencias desde la BD."""
        from app.database import buscar_localidades_por_nombre

        # Si el cambio fue causado por programación interna, ignorarlo
        if getattr(self, "_suppress_input_change", False):
            self._suppress_input_change = False
            return

        if not value or len(value) < 2:
            # no buscar hasta que el usuario escriba 2+ caracteres
            self._localidades_suggestions = []
            if self._localidades_container:
                self._localidades_container.clear()
            return

        suggestions = buscar_localidades_por_nombre(value, limit=10)
        # Guardar sugerencias localmente (lista de dicts with id,nombre,lat,long)
        self._localidades_suggestions = suggestions
        # Renderizar sugerencias en el contenedor
        if self._localidades_container:
            self._localidades_container.clear()
            # Usar el contenedor como contexto para que los elementos se aniden correctamente
            with self._localidades_container:
                if not suggestions:
                    ui.label("No hay sugerencias").classes("text-body2 text-grey-6")
                else:
                    for s in suggestions:
                        # Cada sugerencia es un botón que al pulsar rellena el input y fija
                        # la localidad como origen automáticamente
                        def _make_on_click(item):
                            def _on_click(e=None):
                                # Rellenar input sin disparar el handler
                                self._suppress_input_change = True
                                self.localidad_input.set_value(item.get("nombre"))
                                # Fijar esta sugerencia como localidad origen
                                self.localidad_fijada = {
                                    "id": item.get("id"),
                                    "nombre": item.get("nombre"),
                                    "latitud": item.get("latitud"),
                                    "longitud": item.get("longitud"),
                                }
                                # Limpiar sugerencias y contenedor
                                self._localidades_suggestions = []
                                if self._localidades_container:
                                    self._localidades_container.clear()
                                # Notificar y mostrar mensaje
                                try:
                                    self._notify_change()
                                except Exception:
                                    pass
                                ui.notify(f"Localidad fijada: {item.get('nombre')}", color="positive")
                                # Actualizar badge permanente
                                try:
                                    self._render_badge()
                                except Exception:
                                    pass

                            return _on_click

                        ui.button(s.get("nombre"), on_click=_make_on_click(s)).props("flat")

    def _on_fijar_localidad(self):
        """Fija la primera sugerencia (si existe) como localidad origen."""
        if not self._localidades_suggestions:
            return

        primera = self._localidades_suggestions[0]
        # Guardar la localidad fijada con campos id,nombre,latitud,longitud
        self.localidad_fijada = {
            "id": primera.get("id"),
            "nombre": primera.get("nombre"),
            "latitud": primera.get("latitud"),
            "longitud": primera.get("longitud"),
        }
        # Reflejar en el input sin disparar handler
        self._suppress_input_change = True
        self.localidad_input.set_value(primera.get("nombre"))
        # Limpiar sugerencias y contenedor
        self._localidades_suggestions = []
        if self._localidades_container:
            self._localidades_container.clear()
        ui.notify(f"Localidad fijada: {primera.get('nombre')}", color="positive")
        try:
            self._notify_change()
        except Exception:
            pass
        try:
            self._render_badge()
        except Exception:
            pass

    def _on_limpiar_localidad(self):
        """Limpia la localidad fijada y el input."""
        self.localidad_fijada = None
        if self.localidad_input:
            self.localidad_input.set_value("")
        # Limpiar badge si existe
        try:
            if self._badge_container:
                self._badge_container.clear()
        except Exception:
            pass
        # Notificar cambio para que la app se actualice
        try:
            self._notify_change()
        except Exception:
            pass

    def clear_filters(self):
        """Limpia todos los filtros."""
        self.precio_alquiler.set_value(None)
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
            
            # Fila 5: Localidad Origen (autocomplete)
            with ui.column().classes("gap-2"):
                ui.label("Localidad Origen (cálculo de distancias)").classes("text-caption text-grey-6")
                # Usar input simple y sugerencias dinámicas
                self.localidad_input = ui.input(placeholder="Nombre Localidad").props("style='width: 300px'")
                # Lista de sugerencias (se actualizará on_value_change)
                # on_value_change pasa un objeto event con el valor
                self.localidad_input.on_value_change(lambda e: self._on_localidad_input_change(e.value))

                # Contenedor dinámico para mostrar sugerencias seleccionables
                with ui.column() as self._localidades_container:
                    pass

                with ui.row().classes("gap-2"):
                    ui.button("Limpiar Localidad", on_click=lambda: self._on_limpiar_localidad()).props("flat color=grey")
                # Badge permanente para la localidad fijada (se renderiza cuando existe)
                with ui.row() as self._badge_container:
                    pass

            # Botón limpiar
            ui.button(
                "Limpiar filtros", on_click=self.clear_filters, icon="filter_alt_off"
            ).props("flat color=grey")

        return self._container

    def _render_badge(self):
        """Renderiza un badge permanente con la localidad fijada y botón para limpiarla."""
        if not self._badge_container:
            return
        self._badge_container.clear()
        if not self.localidad_fijada:
            return

        nombre = self.localidad_fijada.get("nombre")
        with self._badge_container:
            with ui.row().classes("items-center gap-2"):
                ui.label("Origen:").classes("text-caption")
                ui.chips([nombre])
                ui.icon("close").on('click', lambda e: self._on_limpiar_localidad())
