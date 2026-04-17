# app/components/detail_dialog.py - Ventana de detalle
"""
Diálogo de detalle de ciudad.
"""

from nicegui import ui
from app.database import get_datos_localidad, get_datos_comparativos, get_connection
from app.database import calcular_puntuacion_100, get_color_categoria
from app.components.score_circle import crear_circulo_puntuacion
from urllib.parse import quote
import plotly.express as px
import plotly.graph_objects as go


def normalizar_wikipedia(nombre: str) -> str:
    """Convierte nombre a minúsculas para Wikipedia."""
    return nombre.lower().replace(" ", "_")


class DetailDialog:
    """Diálogo de detalle de ciudad."""

    def __init__(self):
        self._dialog = None
        self._content = None
        self._hospital_dialog = None
        self._cines_dialog = None
        self._teatros_dialog = None
        self._museos_dialog = None

    def show(self, localidad_id: int):
        """Muestra el diálogo con los datos de la localidad."""
        datos = get_datos_localidad(localidad_id)

        self._content.clear()

        with self._content:
            self._build_header(datos)
            self._build_score_section(datos)
            self._build_general_section(datos)
            self._build_map_section(datos)
            self._build_transporte_section(datos)
            self._build_vivienda_section(datos)
            self._build_sanidad_section(datos, localidad_id)
            self._build_cultura_section(datos, localidad_id)
            self._build_gastos_section(datos)

        self._dialog.open()

    def _build_header(self, datos: dict):
        """Construye el header del diálogo."""
        loc = datos.get("localidad", {})
        nombre = loc.get("nombre", "Desconocido")
        provincia = loc.get("provincia", "")
        comunidad = loc.get("comunidad_autonoma", "")
        wiki_url = (
            f"https://es.wikipedia.org/wiki/{quote(normalizar_wikipedia(nombre))}"
        )

        with ui.row().classes("w-full justify-between items-start mb-4"):
            with ui.column():
                ui.label(nombre).classes("text-h5 font-bold")
                with ui.row().classes("gap-2 items-center"):
                    ui.label(provincia).classes("text-body1 text-grey-7")
                    ui.label("•").classes("text-grey-5")
                    ui.label(comunidad).classes("text-body1 text-grey-7")

            ui.button(
                "Wikipedia",
                icon="open_in_new",
                on_click=lambda: ui.navigate.to(wiki_url, new_tab=True),
            ).props("outline color=primary")

    def _build_score_section(self, datos: dict):
        """Construye la sección de puntuación."""
        calidad = datos.get("calidad_ciudad", {})
        puntuacion = calidad.get("puntuacion")
        categoria = calidad.get("categoria")

        with ui.card().classes("w-full mb-4"):
            with ui.row().classes("w-full items-center gap-8"):
                crear_circulo_puntuacion(puntuacion, categoria, tamano="120px")

                with ui.column():
                    ui.label("Puntuación de Calidad").classes("text-h6 font-medium")
                    ui.label(
                        f"Scoring: {puntuacion if puntuacion is not None else 'N/A'} puntos"
                    ).classes("text-body2")
                    ui.label(f"Categoría: {categoria or 'Sin clasificar'}").classes(
                        "text-body2"
                    )
                    self._build_leyenda()

    def _build_leyenda(self):
        """Construye la leyenda de colores."""
        categorias = [
            ("Alta", "#006400"),
            ("Media-Alta", "#32CD32"),
            ("Media", "#FFD700"),
            ("Media-Baja", "#FF8C00"),
            ("Baja", "#DC143C"),
        ]

        with ui.row().classes("gap-3 mt-2"):
            for nombre, color in categorias:
                with ui.row().classes("gap-1 items-center"):
                    ui.element("span").style(
                        f"width: 12px; height: 12px; background-color: {color}; border-radius: 50%;"
                    )
                    ui.label(nombre).classes("text-caption")

    def _build_general_section(self, datos: dict):
        """Construye la sección de datos generales."""
        loc = datos.get("localidad", {})
        poblacion = loc.get("poblacion")
        latitud = loc.get("latitud")
        longitud = loc.get("longitud")
        altitud = loc.get("altitud")

        # Formatear población con punto como separador de miles
        poblacion_str = f"{poblacion:,.0f}".replace(",", ".") if poblacion else "N/A"

        with ui.card().classes("w-full mb-4"):
            ui.label("Datos Generales").classes("text-h6 font-medium mb-3")

            with ui.grid(columns=4).classes("w-full gap-4"):
                self._add_info_item("Población", poblacion_str)
                self._add_info_item("Latitud", f"{latitud:.4f}" if latitud else "N/A")
                self._add_info_item(
                    "Longitud", f"{longitud:.4f}" if longitud else "N/A"
                )
                self._add_info_item(
                    "Altitud", f"{int(altitud)} m" if altitud else "N/A"
                )

    def _build_map_section(self, datos: dict):
        """Construye la sección de mapa con Plotly."""
        loc = datos.get("localidad", {})
        latitud = loc.get("latitud")
        longitud = loc.get("longitud")
        nombre = loc.get("nombre", "")

        # Verificar que las coordenadas existan y sean válidas
        if latitud is None or latitud == 0 or longitud is None or longitud == 0:
            with ui.card().classes("w-full mb-4"):
                ui.label("Ubicación").classes("text-h6 font-medium mb-3")
                ui.label("Coordenadas no disponibles para esta localidad").classes(
                    "text-body2 text-grey"
                )
            return

        # Detectar zona: Canarias, Baleares o España peninsular
        if latitud < 36:
            # Centro en Canarias
            map_center = dict(lat=28.5, lon=-15.5)
            map_zoom = 5.9
        elif 36 <= latitud <= 41 and 1 <= longitud <= 5:
            # Centro en Baleares
            map_center = dict(lat=39.5, lon=3)
            map_zoom = 5.9
        else:
            # Centro en España peninsular
            map_center = dict(lat=40.5, lon=-3.7)
            map_zoom = 3.6

        with ui.card().classes("w-full mb-4"):
            ui.label("Ubicación").classes("text-h6 font-medium mb-3")

            # Crear figura con Plotly
            fig = go.Figure()
            fig.add_trace(
                go.Scattermap(
                    lat=[latitud],
                    lon=[longitud],
                    mode="markers+text",
                    marker=dict(size=12, color="red", symbol="star"),
                    text=[nombre],
                    textposition="top center",
                    hoverinfo="text",
                    hovertext=f"{nombre}<br>Lat: {latitud:.4f}<br>Lon: {longitud:.4f}",
                )
            )

            fig.update_layout(
                map=dict(
                    style="open-street-map",
                    center=map_center,
                    zoom=map_zoom,
                ),
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                autosize=True,
            )

            # Crear contenedor con estilo para limitar ancho
            with ui.element("div").style(
                "width: 100%; max-width: 100%; overflow: hidden;"
            ):
                ui.plotly(fig)

    def _build_transporte_section(self, datos: dict):
        """Construye la sección de transporte."""
        trans = datos.get("transporte", {})

        if not trans:
            return

        servicios = []
        if trans.get("tiene_ave") or trans.get("tiene_larga_media_distancia"):
            servicios.append("AVE/Media Distancia")
        if trans.get("tiene_cercanias"):
            servicios.append("Cercanías")
        if trans.get("tiene_regional"):
            servicios.append("Regional")
        if trans.get("tiene_aeropuerto"):
            servicios.append("Aeropuerto")

        if not servicios:
            return

        with ui.card().classes("w-full mb-4"):
            ui.label("Transporte").classes("text-h6 font-medium mb-3")
            with ui.row().classes("gap-2 flex-wrap"):
                for svc in servicios:
                    ui.badge(svc, color="primary").props("outline")

    def _build_vivienda_section(self, datos: dict):
        """Construye la sección de vivienda."""
        viv = datos.get("vivienda", {})
        if not viv:
            return

        with ui.card().classes("w-full mb-4"):
            ui.label("Vivienda").classes("text-h6 font-medium mb-3")

            with ui.grid(columns=2).classes("w-full gap-4"):
                # Precio alquiler medio con 2 decimales
                precio = viv.get("precio_alquiler")
                self._add_info_item(
                    "Precio Alquiler medio", f"{precio:.2f} €/mes" if precio else "N/A"
                )
                self._add_info_item(
                    "Precio m²",
                    f"{viv.get('precio_m2', 'N/A')} €/m²"
                    if viv.get("precio_m2")
                    else "N/A",
                )
                self._add_info_item(
                    "Superficie media",
                    f"{viv.get('superficie_media_m2', 'N/A')} m²"
                    if viv.get("superficie_media_m2")
                    else "N/A",
                )
                self._add_info_item(
                    "Viviendas turísticas",
                    f"{viv.get('porcentaje_viviendas_turisticas', 'N/A')}%",
                )

    def _build_sanidad_section(self, datos: dict, localidad_id: int):
        """Construye la sección de sanidad/hospitales."""
        hosp = datos.get("hospitales", {})

        if not hosp or hosp.get("num_hospitales_total", 0) == 0:
            return

        total = hosp.get("num_hospitales_total", 0)

        with ui.card().classes("w-full mb-4"):
            ui.label("Sanidad").classes("text-h6 font-medium mb-3")
            with ui.row().classes("gap-2 items-center"):
                ui.label("Hospitales en la localidad: ").classes("text-body1")
                ui.button(
                    f"{total}",
                    on_click=lambda: self._show_hospitales_detalles(localidad_id),
                    icon="local_hospital",
                ).props("flat color=primary")

    def _show_hospitales_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de hospitales."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre, direccion, codigo_postal, telefono 
            FROM hospital_detalle 
            WHERE localidad_id = ?
        """,
            (localidad_id,),
        )
        hospitales = cursor.fetchall()
        conn.close()

        contenido = self._hospital_dialog._content
        contenido.clear()

        with contenido:
            ui.label("Hospitales de la Localidad").classes("text-h6 font-bold mb-4")

            if not hospitales:
                ui.label("No hay hospitales registrados")
            else:
                for h in hospitales:
                    with ui.card().classes("w-full mb-2 p-3"):
                        ui.label(h["nombre"] or "Sin nombre").classes(
                            "text-body1 font-medium"
                        )
                        if h["direccion"]:
                            ui.label(h["direccion"]).classes("text-body2")
                        if h["codigo_postal"] or h["telefono"]:
                            partes = []
                            if h["codigo_postal"]:
                                partes.append(f"CP: {h['codigo_postal']}")
                            if h["telefono"]:
                                partes.append(f"Telf: {h['telefono']}")
                            ui.label(" | ".join(partes)).classes(
                                "text-body2 text-grey-7"
                            )

        self._hospital_dialog._dialog.open()

    def _build_gastos_section(self, datos: dict):
        """Construye la sección de gastos."""
        gastos_list = datos.get("gastos", [])

        # Filtrar solo los códigos deseados
        codigos_deseados = ["01", "03", "07", "09", "10", "11"]
        nombres_codigos = {
            "01": "Alimentación",
            "03": "Vivienda",
            "07": "Transporte",
            "09": "Ocio y Cultura",
            "10": "Educación",
            "11": "Restaurantes",
        }

        gastos_filtrados = [
            g for g in gastos_list if g.get("codigo_gasto") in codigos_deseados
        ]

        if not gastos_filtrados:
            return

        with ui.card().classes("w-full mb-4"):
            ui.label("Gastos medios en Localidad").classes("text-h6 font-medium mb-3")

            with ui.grid(columns=2).classes("w-full gap-4"):
                for gasto in gastos_filtrados:
                    codigo = gasto.get("codigo_gasto", "")
                    nombre = nombres_codigos.get(
                        codigo, gasto.get("nombre_gasto", "N/A")
                    )
                    mensual = gasto.get("gasto_mensual", "N/A")
                    if mensual and isinstance(mensual, (int, float)):
                        mensual = f"{mensual:.2f} €/mes"
                    self._add_info_item(nombre, str(mensual) if mensual else "N/A")

    def _build_cultura_section(self, datos: dict, localidad_id: int):
        """Construye la sección de cultura y ocio."""
        cult = datos.get("cultura", {})
        if not cult:
            return

        num_cines = cult.get("num_salas_cine", 0)
        num_teatros = cult.get("num_salas_teatro", 0)
        num_museos = cult.get("num_museos", 0)

        with ui.card().classes("w-full mb-4"):
            ui.label("Cultura y Ocio").classes("text-h6 font-medium mb-3")

            with ui.grid(columns=3).classes("w-full gap-4"):
                # Cines - clickeable si > 0
                if num_cines > 0:
                    self._add_clickable_item(
                        "Cines",
                        num_cines,
                        lambda: self._show_cines_detalles(localidad_id),
                    )
                else:
                    self._add_info_item("Cines", "0")

                # Teatros - clickeable si > 0
                if num_teatros > 0:
                    self._add_clickable_item(
                        "Teatros",
                        num_teatros,
                        lambda: self._show_teatros_detalles(localidad_id),
                    )
                else:
                    self._add_info_item("Teatros", "0")

                # Museos - clickeable si > 0
                if num_museos > 0:
                    self._add_clickable_item(
                        "Museos",
                        num_museos,
                        lambda: self._show_museos_detalles(localidad_id),
                    )
                else:
                    self._add_info_item("Museos", "0")

    def _show_cines_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de cines."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre 
            FROM cines_detalle 
            WHERE localidad_id = ?
        """,
            (localidad_id,),
        )
        cines = cursor.fetchall()
        conn.close()

        contenido = self._cines_dialog._content
        contenido.clear()

        with contenido:
            ui.label("Cines de la Localidad").classes("text-h6 font-bold mb-4")

            if not cines:
                ui.label("No hay cines registrados")
            else:
                for c in cines:
                    ui.label(f"• {c['nombre'] or 'Sin nombre'}").classes(
                        "text-body1 mb-1"
                    )

        self._cines_dialog._dialog.open()

    def _show_teatros_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de teatros."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre, direccion, codigo_postal 
            FROM teatros_detalle 
            WHERE localidad_id = ?
        """,
            (localidad_id,),
        )
        teatros = cursor.fetchall()
        conn.close()

        contenido = self._teatros_dialog._content
        contenido.clear()

        with contenido:
            ui.label("Teatros de la Localidad").classes("text-h6 font-bold mb-4")

            if not teatros:
                ui.label("No hay teatros registrados")
            else:
                for t in teatros:
                    with ui.card().classes("w-full mb-2 p-2"):
                        ui.label(t["nombre"] or "Sin nombre").classes(
                            "text-body1 font-medium"
                        )
                        if t["direccion"]:
                            partes = [t["direccion"]]
                            if t["codigo_postal"]:
                                partes.append(f"CP: {t['codigo_postal']}")
                            ui.label(" | ".join(partes)).classes(
                                "text-body2 text-grey-7"
                            )

        self._teatros_dialog._dialog.open()

    def _show_museos_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de museos."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre 
            FROM museos_detalle 
            WHERE localidad_id = ?
        """,
            (localidad_id,),
        )
        museos = cursor.fetchall()
        conn.close()

        contenido = self._museos_dialog._content
        contenido.clear()

        with contenido:
            ui.label("Museos de la Localidad").classes("text-h6 font-bold mb-4")

            if not museos:
                ui.label("No hay museos registrados")
            else:
                for m in museos:
                    ui.label(f"• {m['nombre'] or 'Sin nombre'}").classes(
                        "text-body1 mb-1"
                    )

        self._museos_dialog._dialog.open()

    def _add_info_item(self, label: str, value: str):
        """Agrega un item de información."""
        with ui.column().classes("gap-1"):
            ui.label(label).classes("text-caption text-grey-6")
            ui.label(str(value)).classes("text-body1 font-medium")

    def _add_clickable_item(self, label: str, value: int, on_click: callable):
        """Agrega un item clickeable."""
        with ui.column().classes("gap-1"):
            ui.label(label).classes("text-caption text-grey-6")
            ui.button(str(value), on_click=on_click, icon="info").props(
                "flat color=primary"
            )

    def build(self) -> ui.dialog:
        """Construye el componente UI del diálogo principal."""
        with ui.dialog().props("width=900px") as self._dialog:
            with ui.card():
                with ui.column().classes("gap-4 w-full") as self._content:
                    ui.spinner(size="lg")
                    ui.label("Cargando datos...")

                with ui.card_actions().classes("justify-end"):
                    ui.button("Cerrar", on_click=self._dialog.close).props("color=grey")

        # Crear diálogos auxiliares para detalles
        self._hospital_dialog = self._create_mini_dialog("Hospitales")
        self._cines_dialog = self._create_mini_dialog("Cines")
        self._teatros_dialog = self._create_mini_dialog("Teatros")
        self._museos_dialog = self._create_mini_dialog("Museos")

        return self._dialog

    def _create_mini_dialog(self, title: str):
        """Crea un diálogo pequeño para detalles."""

        class MiniDialog:
            def __init__(self):
                self._dialog = None
                self._content = None

        mini = MiniDialog()
        with ui.dialog().props("width=400px") as mini._dialog:
            with ui.card():
                with ui.column().classes(
                    "gap-2 max-h-96 overflow-auto"
                ) as mini._content:
                    pass
                with ui.card_actions().classes("justify-end"):
                    ui.button("Cerrar", on_click=mini._dialog.close).props(
                        "flat color=grey"
                    )

        return mini
