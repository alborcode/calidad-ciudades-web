# app/components/detail_dialog.py - Ventana de detalle
"""
Diálogo de detalle de ciudad.
"""

from nicegui import ui
from app.database import get_datos_localidad, get_datos_comparativos, get_connection
from app.database import (
    calcular_puntuacion_100,
    get_color_categoria,
    get_categoria_from_score,
)
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
        self._bibliotecas_dialog = None
        self._universidades_dialog = None
        self._current_datos = None  # Para guardar datos actuales entre llamadas
        self._origen_getter = None

    def show(self, localidad_id: int):
        """Muestra el diálogo con los datos de la localidad."""
        datos = get_datos_localidad(localidad_id)
        self._current_datos = datos  # Guardar para usar en _show_universidades_detalles

        self._content.clear()

        with self._content:
            self._build_header(datos)
            self._build_score_section(datos)
            self._build_general_section(datos)
            self._build_map_section(datos)
            # Clima justo después de Ubicación (map) / antes de Administración
            self._build_clima_section(datos)
            self._build_admin_section(datos)
            self._build_vivienda_section(datos)
            self._build_transporte_section(datos)
            self._build_sanidad_section(datos, localidad_id)
            self._build_cultura_section(datos, localidad_id)
            self._build_educacion_section(datos, localidad_id)
            self._build_gastos_section(datos)
            self._build_paro_section(datos)
            self._build_renta_section(datos)
            self._build_delincuencia_section(datos)

        self._dialog.open()

    def set_origen_getter(self, getter: callable):
        """Registra un callable que retorna la localidad origen fijada (o None).

        El callable debe devolver un dict con claves: id,nombre,latitud,longitud o None.
        """
        self._origen_getter = getter

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
                    
                    # Si existe localidad origen y coordenadas, mostrar distancia
                    try:
                        if self._origen_getter:
                            origen = self._origen_getter()
                        else:
                            origen = None
                    except Exception:
                        origen = None

                    lat = loc.get("latitud")
                    lon = loc.get("longitud")
                    if origen and origen.get("latitud") and lat:
                        from app.utils.geo import haversine

                        dist_km = haversine(float(origen.get("latitud")), float(origen.get("longitud")), float(lat), float(lon))
                        # Mostrar sin decimales
                        ui.label(f"Distancia a localidad origen: {int(round(dist_km))} km").classes("text-body2 text-grey-6")

            ui.button(
                "Wikipedia",
                icon="open_in_new",
                on_click=lambda: ui.navigate.to(wiki_url, new_tab=True),
            ).props("outline color=primary")

    def _build_score_section(self, datos: dict):
        """Construye la sección de puntuación."""
        calidad = datos.get("calidad_ciudad", {})
        puntuacion = calidad.get("puntuacion")
        categoria_db = calidad.get("categoria")  # Categoría de la BD (vieja)

        # Calcular categoría basada en puntuación 100 (nueva escala 28=100)
        puntuacion_100 = calcular_puntuacion_100(puntuacion)
        categoria = get_categoria_from_score(puntuacion_100)

        with ui.card().classes("w-full mb-4"):
            ui.label("Puntuación de Calidad").classes("text-h6 font-medium mb-3")
            with ui.column().classes("items-center"):
                crear_circulo_puntuacion(puntuacion, categoria, tamano="120px")
            with ui.column().classes("mt-3"):
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
        trans_urbano = datos.get("transporte_urbano", {})

        # Recopilar todos los servicios de transporte
        servicios = []

        if trans.get("tiene_ave") or trans.get("tiene_larga_media_distancia"):
            servicios.append("AVE/Media Distancia")
        if trans.get("tiene_cercanias"):
            servicios.append("Cercanías")
        if trans.get("tiene_regional"):
            servicios.append("Regional")
        if trans.get("tiene_aeropuerto"):
            servicios.append("Aeropuerto")

        # Transporte urbano
        if trans_urbano.get("tiene_metro"):
            servicios.append("Metro")
        if trans_urbano.get("tiene_autobus_municipal"):
            servicios.append("Autobús municipal")
        if trans_urbano.get("tiene_tranvia"):
            servicios.append("Tranvía")

        if not servicios:
            return

        # Obtener ID de la localidad para buscar datos de detalle
        loc = datos.get("localidad", {})
        localidad_id = loc.get("id")

        with ui.card().classes("w-full mb-4"):
            ui.label("Transporte").classes("text-h6 font-medium mb-3")
            with ui.row().classes("gap-2 flex-wrap"):
                for svc in servicios:
                    color = "primary"
                    # Metro, Autobús y Tranvía usan color diferente (transporte urbano)
                    if svc in ("Metro", "Autobús municipal", "Tranvía"):
                        color = "amber-8"

                    # Crear badge clickeable para transporte urbano
                    if svc == "Metro" and localidad_id:
                        ui.badge(svc, color=color).props("outline").on('click', lambda e, lid=localidad_id: self._show_metro_detail(lid))
                    elif svc == "Autobús municipal" and localidad_id:
                        ui.badge(svc, color=color).props("outline").on('click', lambda e, lid=localidad_id: self._show_autobus_detail(lid))
                    elif svc == "Tranvía" and localidad_id:
                        ui.badge(svc, color=color).props("outline").on('click', lambda e, lid=localidad_id: self._show_tranvia_detail(lid))
                    else:
                        ui.badge(svc, color=color).props("outline")

    def _build_admin_section(self, datos: dict):
        """Construye la sección de administración."""
        admin = datos.get("administracion", {})

        if not admin:
            return

        organismos = []
        if admin.get("tiene_aeat"):
            organismos.append("AEAT")
        if admin.get("tiene_delegacion_hacienda"):
            organismos.append("Hacienda")
        if admin.get("tiene_seguridad_social"):
            organismos.append("Seguridad Social")
        if admin.get("tiene_aemet"):
            organismos.append("AEMET")
        if admin.get("tiene_plazas_csic"):
            organismos.append("CSIC")
        if admin.get("tiene_plazas_defensa"):
            organismos.append("Defensa")
        if admin.get("tiene_plazas_sepe"):
            organismos.append("SEPE")
        if admin.get("tiene_plazas_imserso"):
            organismos.append("IMSERSO")
        if admin.get("tiene_plazas_cultura"):
            organismos.append("Cultura")
        if admin.get("tiene_plazas_ine"):
            organismos.append("INE")
        if admin.get("tiene_deleg_comercio"):
            organismos.append("Comercio")
        if admin.get("tiene_plazas_educacion"):
            organismos.append("Educación")
        if admin.get("tiene_plazas_justicia"):
            organismos.append("Justicia")
        if admin.get("tiene_plazas_deleg_gobierno"):
            organismos.append("Deleg. Gobierno")
        if admin.get("tiene_plazas_sanidad"):
            organismos.append("Sanidad")
        if admin.get("tiene_demarcacion_carreteras"):
            organismos.append("Carreteras")
        if admin.get("tiene_marina_mercante"):
            organismos.append("Marina Mercante")
        if admin.get("tiene_plazas_dgt"):
            organismos.append("DGT")
        if admin.get("tiene_plazas_policia"):
            organismos.append("Policía")
        if admin.get("tiene_plazas_muface"):
            organismos.append("MUGEFU")

        if not organismos:
            return

        with ui.card().classes("w-full mb-4"):
            ui.label("Administración").classes("text-h6 font-medium mb-3")
            with ui.row().classes("gap-2 flex-wrap"):
                for org in organismos:
                    ui.badge(org, color="secondary").props("outline")

    def _build_vivienda_section(self, datos: dict):
        """Construye la sección de vivienda."""
        viv = datos.get("vivienda", {})
        if not viv:
            return

        # Obtener medias nacionales
        medias = datos.get("medias_nacionales", {})
        precio_m2_nac = medias.get("precio_m2", None)
        superficie_nac = medias.get("superficie_media_m2", None)
        pct_turistica_nac = medias.get("VIVIENDA_TURISTICA_PORCENTAJE", None)

        # Calcular precio alquiler medio nacional: precio_m2 * superficie_media
        precio_alq_nac = None
        if precio_m2_nac is not None and superficie_nac is not None:
            precio_alq_nac = precio_m2_nac * superficie_nac

        # Obtener valores locales
        precio_alq = viv.get("precio_alquiler")
        precio_m2 = viv.get("precio_m2")
        superficie = viv.get("superficie_media_m2")
        pct_turistica = viv.get("porcentaje_viviendas_turisticas")

        # Función auxiliar para determinar color según comparación
        def get_color_comparison(local_val, national_val, invert=False):
            """Retorna color: rojo si mayor, naranja si igual, verde si menor."""
            if local_val is None or national_val is None or national_val == 0:
                return None
            if local_val > national_val:
                return "red-7" if not invert else "green-9"
            elif local_val < national_val:
                return "green-9" if not invert else "red-7"
            else:
                return "orange-7"

        with ui.card().classes("w-full mb-4"):
            ui.label("Vivienda").classes("text-h6 font-medium mb-3")

            with ui.grid(columns=2).classes("w-full gap-4"):
                # Precio Alquiler medio
                precio_color = get_color_comparison(precio_alq, precio_alq_nac)
                self._add_info_item(
                    "Precio Alquiler medio",
                    f"{precio_alq:.2f} €/mes" if precio_alq is not None else "N/A",
                    color=precio_color,
                )

                # Precio m²
                precio_m2_color = get_color_comparison(precio_m2, precio_m2_nac)
                self._add_info_item(
                    "Precio m²",
                    f"{precio_m2:.2f} €/m²" if precio_m2 is not None else "N/A",
                    color=precio_m2_color,
                )

                # Superficie media (invertido: mayor es mejor)
                superficie_color = get_color_comparison(superficie, superficie_nac, invert=True)
                self._add_info_item(
                    "Superficie media",
                    f"{superficie:.1f} m²" if superficie is not None else "N/A",
                    color=superficie_color,
                )

                # % Viviendas turísticas
                turistica_color = get_color_comparison(pct_turistica, pct_turistica_nac)
                self._add_info_item(
                    "Viviendas turísticas",
                    f"{pct_turistica:.2f}%" if pct_turistica is not None else "N/A",
                    color=turistica_color,
                )

    def _build_clima_section(self, datos: dict):
        """Construye la sección de clima."""
        clima = datos.get("clima", {})
        if not clima:
            return

        with ui.card().classes("w-full mb-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("wb_sunny")
                ui.label("Clima").classes("text-h6 font-medium")

            with ui.grid(columns=3).classes("w-full gap-3"):
                temp_med = clima.get("temperatura_media")
                precipit = clima.get("precipitaciones")
                viento = clima.get("viento")

                # Para clima: por defecto no coloreamos temperatura (neutral),
                # para precipitaciones y viento consideramos que menos es mejor.
                from app.utils.visuals import compare_to_national
                medias = datos.get("medias_nacionales", {})
                temp_nac = medias.get("temperatura_media", None)
                precipit_nac = medias.get("precipitaciones_media", None)
                viento_nac = medias.get("viento_media", None)

                temp_color = None
                precipit_color = compare_to_national(
                    precipit, precipit_nac, better_when_higher=False, thresholds=(0.9, 1.1)
                )
                viento_color = compare_to_national(
                    viento, viento_nac, better_when_higher=False, thresholds=(0.9, 1.1)
                )

                self._add_info_item("Temp. media", f"{temp_med:.1f}°C" if temp_med is not None else "N/A", color=temp_color)
                self._add_info_item("Precipit.", f"{precipit:.0f}mm" if precipit is not None else "N/A", color=precipit_color)
                self._add_info_item("Viento", f"{viento:.1f}km/h" if viento is not None else "N/A", color=viento_color)

    def _build_paro_section(self, datos: dict):
        """Construye la sección de desempleo."""
        from app.database import get_connection

        paro = datos.get("paro", {})
        if not paro:
            return

        # Obtener media nacional
        medias = datos.get("medias_nacionales", {})
        tasa_nacional = medias.get("tasa_paro_media", None)

        tasa_local = paro.get("tasa_desempleo", None)
        evolucion = paro.get("variacion_desempleo", None)

        with ui.card().classes("w-full mb-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("trending_down")
                ui.label("Paro").classes("text-h6 font-medium")

            with ui.grid(columns=2).classes("w-full gap-3"):
                # Color basado en helper compare_to_national
                from app.utils.visuals import compare_to_national

                color = compare_to_national(
                    tasa_local, tasa_nacional, better_when_higher=False, thresholds=(0.9, 1.1)
                )

                self._add_info_item(
                    "Tasa desempleo",
                    f"{tasa_local:.1f}%" if tasa_local is not None else "N/A",
                    color=color,
                )
                self._add_info_item(
                    "Evolución trim.", f"{evolucion:+.1f}%" if evolucion is not None else "N/A"
                )

                if tasa_nacional is not None:
                    self._add_info_item("Media nac.", f"{tasa_nacional:.1f}%")

    def _build_renta_section(self, datos: dict):
        """Construye la sección de renta."""
        from app.database import get_connection

        renta = datos.get("renta", {})
        if not renta:
            return

        # Obtener media nacional
        medias = datos.get("medias_nacionales", {})
        renta_nacional = medias.get("renta_bruta_media", 0)

        bruta = renta.get("renta_bruta_media", 0)
        neta = renta.get("renta_neta_media", 0)
        var_bruta = renta.get("variacion_renta_bruta", 0)

        with ui.card().classes("w-full mb-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("account_balance_wallet")
                ui.label("Renta").classes("text-h6 font-medium")

            with ui.grid(columns=2).classes("w-full gap-3"):
                # Color basado en helper compare_to_national (renta: más es mejor)
                from app.utils.visuals import compare_to_national

                color = compare_to_national(
                    bruta, renta_nacional, better_when_higher=True, thresholds=(0.9, 1.1)
                )

                self._add_info_item(
                    "Renta bruta", f"{bruta:,.0f}€" if bruta is not None else "N/A", color=color
                )
                self._add_info_item("Renta neta", f"{neta:,.0f}€" if neta is not None else "N/A")
                self._add_info_item("Var. brut.", f"{var_bruta:+.1f}%" if var_bruta is not None else "N/A")

                if renta_nacional is not None:
                    self._add_info_item("Media nac.", f"{renta_nacional:,.0f}€")

    def _build_delincuencia_section(self, datos: dict):
        """Construye la sección de delitos."""
        from app.database import get_connection

        delitos = datos.get("delitos", {})
        if not delitos:
            return

        # Obtener media nacional
        medias = datos.get("medias_nacionales", {})
        tasa_nacional = medias.get("tasa_criminalidad_media", 0)

        tasa_local = delitos.get("tasa_criminalidad_convencional", 0)
        total = delitos.get("numero_criminalidad_convencional", 0)

        with ui.card().classes("w-full mb-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("warning")
                ui.label("Seguridad").classes("text-h6 font-medium")

            with ui.grid(columns=2).classes("w-full gap-3"):
                # Color basado en helper compare_to_national (delincuencia: menos es mejor)
                from app.utils.visuals import compare_to_national

                color = compare_to_national(
                    tasa_local, tasa_nacional, better_when_higher=False, thresholds=(0.8, 1.2), tokens=("positive", "warning", "negative")
                )

                self._add_info_item(
                    "Tasa crimes", f"{tasa_local:.1f}" if tasa_local is not None else "N/A", color=color
                )
                self._add_info_item("Total crimes", str(total) if total else "N/A")

                if tasa_nacional is not None:
                    self._add_info_item("Media nac.", f"{tasa_nacional:.1f}")

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
            with ui.row().classes("items-center gap-2"):
                ui.icon("local_hospital")
                ui.label("Hospitales de la Localidad").classes("text-h6 font-bold")

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

    def _build_educacion_section(self, datos: dict, localidad_id: int):
        """Construye la sección de educación (bibliotecas y universidades)."""
        calidad = datos.get("calidad_ciudad", {})

        # Bibliotecas: nota_bibliotecas indica si hay bibliotecas
        nota_bibliotecas = calidad.get("nota_bibliotecas", 0)

        # Mostrar siempre la sección de educación (aunque sea 0, se mostrará "0")
        with ui.card().classes("w-full mb-4"):
            ui.label("Educación").classes("text-h6 font-medium mb-3")

            with ui.grid(columns=2).classes("w-full gap-4"):
                # Bibliotecas - clickeable si hay
                if nota_bibliotecas > 0:
                    self._add_clickable_item(
                        "Bibliotecas",
                        nota_bibliotecas,
                        lambda: self._show_bibliotecas_detalles(localidad_id),
                        icon="menu_book",
                    )
                else:
                    self._add_info_item("Bibliotecas", "0")

                # Universidades - siempre clickeable si hay datos
                # Consultar directamente la tabla universidades_detalle
                loc = datos.get("localidad", {})
                codigo_ine = loc.get("codigo_ine")

                conn = get_connection()
                cursor = conn.cursor()
                if codigo_ine:
                    cursor.execute(
                        "SELECT COUNT(*) FROM universidades_detalle WHERE codigo_municipio_ine = ?",
                        (codigo_ine,),
                    )
                    num_universidades = cursor.fetchone()[0]
                else:
                    num_universidades = 0
                conn.close()

                if num_universidades > 0:
                    self._add_clickable_item(
                        "Universidades",
                        num_universidades,
                        lambda: self._show_universidades_detalles(localidad_id),
                        icon="school",
                    )
                else:
                    self._add_info_item("Universidades", "0")

    def _show_bibliotecas_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de bibliotecas."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre, institucion, direccion, codigo_postal, tipo_biblioteca, tipo_dependencia
            FROM biblioteca_detalle 
            WHERE localidad_id = ?
            ORDER BY nombre
        """,
            (localidad_id,),
        )
        bibliotecas = cursor.fetchall()
        conn.close()

        contenido = self._bibliotecas_dialog._content
        contenido.clear()

        with contenido:
            with ui.row().classes("items-center gap-2"):
                ui.icon("menu_book")
                ui.label("Bibliotecas de la Localidad").classes("text-h6 font-bold")

            if not bibliotecas:
                ui.label("No hay bibliotecas registradas")
            else:
                for b in bibliotecas:
                    nombre = b["nombre"] or "Sin nombre"
                    institucion = b["institucion"]
                    direccion = b["direccion"]
                    cp = b["codigo_postal"]
                    tipo = b["tipo_biblioteca"]
                    dependencia = b["tipo_dependencia"]

                    with ui.card().classes("w-full mb-2 p-2"):
                        ui.label(nombre).classes("text-body1 font-medium")
                        if institucion:
                            ui.label(f"Institución: {institucion}").classes(
                                "text-caption text-grey-7"
                            )
                        if tipo:
                            ui.label(f"Tipo: {tipo}").classes("text-body2")
                        if dependencia:
                            ui.label(f"Dependencia: {dependencia}").classes(
                                "text-body2"
                            )
                        if direccion:
                            dir_text = f"Dirección: {direccion}"
                            if cp:
                                dir_text += f" ({cp})"
                            ui.label(dir_text).classes("text-body2")
                        else:
                            ui.label("Dirección: No disponible").classes(
                                "text-body2 text-grey-5"
                            )

        self._bibliotecas_dialog._dialog.open()

    def _show_universidades_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de universidades."""
        loc = self._current_datos.get("localidad", {})
        codigo_ine = loc.get("codigo_ine")

        if not codigo_ine:
            # No se puede mostrar si no hay código INE
            ui.notify("No hay código INE para esta localidad", color="warning")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre, anno_fundacion, tipo, es_sede_principal, sitio_web, provincia, comunidad_autonoma
            FROM universidades_detalle
            WHERE codigo_municipio_ine = ?
            ORDER BY nombre
        """,
            (codigo_ine,),
        )
        universidades = cursor.fetchall()
        conn.close()

        with ui.dialog() as dialog, ui.card().classes("q-pa-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("school")
                ui.label("Universidades de la Localidad").classes("text-h6 font-medium")

            if not universidades:
                ui.label("No hay universidades registradas")
            else:
                with ui.column().classes("w-full gap-3 mt-3"):
                    for u in universidades:
                        nombre = u[0] or "Sin nombre"
                        anno = u[1]
                        tipo = u[2] or "No especificado"
                        es_principal = u[3]
                        url = u[4]
                        provincia = u[5]
                        comunidad = u[6]

                        with ui.card().classes("w-full"):
                            ui.label(f"{nombre}").classes("text-body1 font-medium")
                            info = f"Año: {anno or 'N/A'} | Tipo: {tipo}"
                            if es_principal:
                                info += " (Sede principal)"
                            ui.label(info).classes("text-body2 text-grey-7")
                            if provincia or comunidad:
                                ui.label(f"Ubicación: {provincia or ''}, {comunidad or ''}").classes("text-body2 text-grey-7")
                            if url:
                                ui.button(
                                    "Web",
                                    on_click=lambda e, uurl=url: ui.navigate.to(uurl, new_tab=True),
                                    icon="open_in_new",
                                ).props("flat color=primary size=sm")

            with ui.row().classes("mt-4 justify-end"):
                ui.button("Cerrar", on_click=dialog.close).props("flat color=grey")

        dialog.open()

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
                        icon="movie",
                    )
                else:
                    self._add_info_item("Cines", "0")

                # Teatros - clickeable si > 0
                if num_teatros > 0:
                    self._add_clickable_item(
                        "Teatros",
                        num_teatros,
                        lambda: self._show_teatros_detalles(localidad_id),
                        icon="theater_comedy",
                    )
                else:
                    self._add_info_item("Teatros", "0")

                # Museos - clickeable si > 0
                if num_museos > 0:
                    self._add_clickable_item(
                        "Museos",
                        num_museos,
                        lambda: self._show_museos_detalles(localidad_id),
                        icon="museum",
                    )
                else:
                    self._add_info_item("Museos", "0")

    def _show_cines_detalles(self, localidad_id: int):
        """Muestra el diálogo con detalles de cines."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre_cine, numero_pantallas, nombre_municipio
            FROM cines_detalle 
            WHERE localidad_id = ?
            ORDER BY numero_pantallas DESC
        """,
            (localidad_id,),
        )
        cines = cursor.fetchall()
        conn.close()

        contenido = self._cines_dialog._content
        contenido.clear()

        with contenido:
            with ui.row().classes("items-center gap-2"):
                ui.icon("movie")
                ui.label("Cines de la Localidad").classes("text-h6 font-bold")

            if not cines:
                ui.label("No hay cines registrados")
            else:
                for c in cines:
                    nombre = c["nombre_cine"] or "Sin nombre"
                    pantallas = c["numero_pantallas"]

                    with ui.card().classes("w-full mb-2 p-2"):
                        ui.label(nombre).classes("text-body1 font-medium")
                        ui.label(f"Pantallas: {pantallas}").classes("text-body2")
                        if c["nombre_municipio"]:
                            ui.label(f"Municipio: {c['nombre_municipio']}").classes(
                                "text-caption text-grey-7"
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
            with ui.row().classes("items-center gap-2"):
                ui.icon("theater_comedy")
                ui.label("Teatros de la Localidad").classes("text-h6 font-bold")

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
            SELECT nombre, direccion, telefono, tipo 
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
            with ui.row().classes("items-center gap-2"):
                ui.icon("museum")
                ui.label("Museos de la Localidad").classes("text-h6 font-bold")

            if not museos:
                ui.label("No hay museos registrados")
            else:
                for m in museos:
                    nombre = m["nombre"] or "Sin nombre"
                    direccion = m["direccion"]
                    telefono = m["telefono"]
                    tipo = m["tipo"]

                    # Tarjeta del museo
                    with ui.card().classes("w-full mb-2 p-2"):
                        ui.label(nombre).classes("text-body1 font-medium")
                        if tipo:
                            ui.label(f"Tipo: {tipo}").classes(
                                "text-caption text-grey-7"
                            )
                        if direccion:
                            ui.label(f"Dirección: {direccion}").classes("text-body2")
                        if telefono:
                            ui.label(f"Teléfono: {telefono}").classes("text-body2")
                        else:
                            ui.label("Teléfono: No disponible").classes(
                                "text-body2 text-grey-5"
                            )

        self._museos_dialog._dialog.open()

    def _add_info_item(self, label: str, value: str, color: str = None):
        """Agrega un item de información."""
        with ui.column().classes("gap-1"):
            ui.label(label).classes("text-caption text-grey-6")
            if color:
                # Usar clase CSS de Quasar para color de texto
                ui.label(str(value)).classes(f"text-{color} text-body1 font-medium")
            else:
                ui.label(str(value)).classes("text-body1 font-medium")

    def _add_clickable_item(self, label: str, value: int, on_click: callable, icon: str = "info"):
        """Agrega un item clickeable."""
        with ui.column().classes("gap-1"):
            ui.label(label).classes("text-caption text-grey-6")
            ui.button(str(value), on_click=on_click, icon=icon).props(
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
        self._bibliotecas_dialog = self._create_mini_dialog("Bibliotecas")
        self._universidades_dialog = self._create_mini_dialog("Universidades")

        return self._dialog

    def _create_mini_dialog(self, title: str):
        """Crea un diálogo para detalles."""

        class MiniDialog:
            def __init__(self):
                self._dialog = None
                self._content = None

        mini = MiniDialog()
        with ui.dialog().props("width=600px") as mini._dialog:
            with ui.card().classes("q-pa-md"):
                with ui.column().classes(
                    "gap-3"
                ) as mini._content:
                    pass
                with ui.card_actions().classes("justify-end"):
                    ui.button("Cerrar", on_click=mini._dialog.close).props(
                        "flat color=grey"
                    )

        return mini

    def _show_metro_detail(self, localidad_id: int):
        """Muestra ventana de leyenda con datos de Metro."""
        from app.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre_comercial, ano_inauguracion, numero_lineas, estaciones, kilometros "
            "FROM metros_detalle WHERE codigo_municipio_ine = "
            "(SELECT codigo_ine FROM localidades WHERE id = ?)",
            (localidad_id,),
        )
        metros = cursor.fetchall()
        conn.close()

        if not metros:
            ui.notify("No hay datos de Metro para esta localidad", color="warning")
            return

        with ui.dialog().props("width=500px"), ui.card().classes("q-pa-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("subway")
                ui.label("Metro").classes("text-h6 font-medium")
            with ui.list().classes("w-full mt-3"):
                for row in metros:
                    nombre, ano, lineas, estaciones_km, km = row
                    with ui.list_item():
                        with ui.column().classes("w-full gap-1"):
                            ui.label(f"{nombre}").classes("text-body1 font-medium")
                            info = f"Año: {ano or 'N/A'} | Líneas: {lineas or 'N/A'} | Estaciones: {estaciones_km or 'N/A'} | Km: {km or 'N/A'}"
                            ui.label(info).classes("text-body2 text-grey-7")
            with ui.row().classes("mt-4 justify-end"):
                ui.button("Cerrar", on_click=lambda: ui.notify("Cerrar")).props("flat")

        # Abrir mini-diálogo existente en lugar de crear uno nuevo cada vez
        self._metro_dialog = self._create_mini_dialog("Metro")
        self._metro_dialog._dialog.open()

    def _show_autobus_detail(self, localidad_id: int):
        """Muestra ventana de leyenda con datos de Autobuses."""
        from app.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT denominacion_comercial, nombre_completo, sistema_gestion "
            "FROM autobuses_detalle WHERE codigo_municipio_ine = "
            "(SELECT codigo_ine FROM localidades WHERE id = ?)",
            (localidad_id,),
        )
        autobuses = cursor.fetchall()
        conn.close()

        if not autobuses:
            ui.notify("No hay datos de Autobuses para esta localidad", color="warning")
            return

        with ui.dialog().props("width=500px"), ui.card().classes("q-pa-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("directions_bus")
                ui.label("Autobuses municipales").classes("text-h6 font-medium")
            with ui.list().classes("w-full mt-3"):
                for row in autobuses:
                    denom, nombre, sistema = row
                    with ui.list_item():
                        with ui.column().classes("w-full gap-1"):
                            ui.label(f"{denom}").classes("text-body1 font-medium")
                            ui.label(f"{nombre}").classes("text-body2 text-grey-7")
                            if sistema:
                                ui.label(f"Sistema: {sistema}").classes("text-body2 text-grey-7")
            with ui.row().classes("mt-4 justify-end"):
                ui.button("Cerrar", on_click=lambda: ui.notify("Cerrar")).props("flat")

        self._autobus_dialog = self._create_mini_dialog("Autobuses")
        self._autobus_dialog._dialog.open()

    def _show_tranvia_detail(self, localidad_id: int):
        """Muestra ventana de leyenda con datos de Tranvías."""
        from app.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT red, tranvia_servicio, numero_lineas, longitud_total "
            "FROM tranvias_detalle WHERE codigo_municipio_ine = "
            "(SELECT codigo_ine FROM localidades WHERE id = ?)",
            (localidad_id,),
        )
        tranvias = cursor.fetchall()
        conn.close()

        if not tranvias:
            ui.notify("No hay datos de Tranvías para esta localidad", color="warning")
            return

        with ui.dialog().props("width=500px"), ui.card().classes("q-pa-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("tram")
                ui.label("Tranvías").classes("text-h6 font-medium")
            with ui.list().classes("w-full mt-3"):
                for row in tranvias:
                    red, servicio, lineas, km = row
                    with ui.list_item():
                        with ui.column().classes("w-full gap-1"):
                            ui.label(f"{red}").classes("text-body1 font-medium")
                            info = f"Líneas: {lineas or 'N/A'} | Longitud: {km or 'N/A'} km"
                            ui.label(info).classes("text-body2 text-grey-7")
            with ui.row().classes("mt-4 justify-end"):
                ui.button("Cerrar", on_click=lambda: ui.notify("Cerrar")).props("flat")

        self._tranvia_dialog = self._create_mini_dialog("Tranvías")
        self._tranvia_dialog._dialog.open()
