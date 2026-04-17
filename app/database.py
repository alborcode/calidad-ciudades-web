# app/database.py - Conexión SQLite y queries
"""
Módulo de base de datos para Calidad Ciudades.
Proporciona conexión y queries a la BD SQLite.
"""

import sqlite3
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass

# Ruta a la base de datos
DB_PATH = Path(__file__).parent.parent / "data" / "calidad_ciudades.db"

# Rango de puntuación en la BD (mínimo y máximo real)
SCORE_MIN = -2
SCORE_MAX = 18


@dataclass
class CiudadFiltro:
    """Filtros para búsqueda de ciudades."""

    precio_alquiler_max: Optional[float] = None
    gasto_alimentacion_max: Optional[float] = None
    tiene_cines: bool = False
    tiene_teatros: bool = False
    tiene_museos: bool = False
    es_costa: bool = False
    tiene_transporte_urbano: bool = False
    tiene_hospital: bool = False
    tiene_universidad: bool = False


@dataclass
class CiudadResultado:
    """Resultado de búsqueda de ciudad."""

    id: int
    localidad: str
    provincia: str
    comunidad: str
    puntuacion: Optional[int]
    categoria: Optional[str]
    precio_alquiler: Optional[float]
    gasto_alimentacion: Optional[float]


def get_connection() -> sqlite3.Connection:
    """Obtiene conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def buscar_ciudades(filtro: CiudadFiltro) -> list[CiudadResultado]:
    """
    Busca ciudades según los filtros especificados.
    Retorna lista ordenada por puntuación descendente.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            l.id,
            l.nombre AS localidad,
            p.nombre_provincia AS provincia,
            c.nombre_comunidad AS comunidad,
            cc.puntuacion,
            cc.categoria,
            v.precio_alquiler,
            g.gasto_mensual AS gasto_alimentacion
        FROM localidades l
        LEFT JOIN calidad_ciudad cc ON l.id = cc.localidad_id
        LEFT JOIN vivienda v ON l.id = v.localidad_id
        LEFT JOIN gastos g ON l.id = g.localidad_id AND g.codigo_gasto = '01'
        LEFT JOIN param_provincias p ON l.codigo_provincia = p.codigo_provincia
        LEFT JOIN param_comunidades c ON p.codigo_comunidad = c.codigo_comunidad
        WHERE 1=1
    """

    params: list[Any] = []

    # Filtro precio alquiler
    if filtro.precio_alquiler_max is not None:
        query += " AND v.precio_alquiler <= ?"
        params.append(filtro.precio_alquiler_max)

    # Filtro gasto alimentación
    if filtro.gasto_alimentacion_max is not None:
        query += " AND g.gasto_mensual <= ?"
        params.append(filtro.gasto_alimentacion_max)

    # Filtros booleanos (solo aplicar si están marcados)
    if filtro.tiene_cines:
        query += " AND EXISTS (SELECT 1 FROM cultura cu WHERE cu.localidad_id = l.id AND cu.num_salas_cine > 0)"

    if filtro.tiene_teatros:
        query += " AND EXISTS (SELECT 1 FROM cultura cu WHERE cu.localidad_id = l.id AND cu.num_salas_teatro > 0)"

    if filtro.tiene_museos:
        query += " AND EXISTS (SELECT 1 FROM cultura cu WHERE cu.localidad_id = l.id AND cu.num_museos > 0)"

    if filtro.es_costa:
        query += " AND EXISTS (SELECT 1 FROM calidad_ciudad cc2 WHERE cc2.localidad_id = l.id AND cc2.nota_costa = 1)"

    if filtro.tiene_transporte_urbano:
        query += """ AND EXISTS (
            SELECT 1 FROM transporte_urbano tu 
            WHERE tu.localidad_id = l.id 
            AND (tu.tiene_metro = 1 OR tu.tiene_autobus_municipal = 1 OR tu.tiene_tranvia = 1)
        )"""

    if filtro.tiene_hospital:
        query += " AND EXISTS (SELECT 1 FROM hospitales h WHERE h.localidad_id = l.id AND h.num_hospitales_total > 0)"

    if filtro.tiene_universidad:
        query += " AND EXISTS (SELECT 1 FROM calidad_ciudad cc3 WHERE cc3.localidad_id = l.id AND cc3.nota_universidad > 0)"

    query += " ORDER BY cc.puntuacion DESC NULLS LAST"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        CiudadResultado(
            id=row["id"],
            localidad=row["localidad"],
            provincia=row["provincia"] or "",
            comunidad=row["comunidad"] or "",
            puntuacion=row["puntuacion"],
            categoria=row["categoria"],
            precio_alquiler=row["precio_alquiler"],
            gasto_alimentacion=row["gasto_alimentacion"],
        )
        for row in rows
    ]


def get_datos_localidad(localidad_id: int) -> dict[str, Any]:
    """Obtiene todos los datos de una localidad."""
    conn = get_connection()
    cursor = conn.cursor()

    datos: dict[str, Any] = {}

    cursor.execute("SELECT * FROM localidades WHERE id = ?", (localidad_id,))
    row = cursor.fetchone()
    if row:
        datos["localidad"] = dict(row)

    cursor.execute(
        "SELECT * FROM calidad_ciudad WHERE localidad_id = ?", (localidad_id,)
    )
    row = cursor.fetchone()
    if row:
        datos["calidad_ciudad"] = dict(row)

    cursor.execute("SELECT * FROM vivienda WHERE localidad_id = ?", (localidad_id,))
    row = cursor.fetchone()
    if row:
        datos["vivienda"] = dict(row)

    cursor.execute("SELECT * FROM gastos WHERE localidad_id = ?", (localidad_id,))
    datos["gastos"] = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM hospitales WHERE localidad_id = ?", (localidad_id,))
    row = cursor.fetchone()
    if row:
        datos["hospitales"] = dict(row)

    cursor.execute("SELECT * FROM transporte WHERE localidad_id = ?", (localidad_id,))
    row = cursor.fetchone()
    if row:
        datos["transporte"] = dict(row)

    cursor.execute(
        "SELECT * FROM transporte_urbano WHERE localidad_id = ?", (localidad_id,)
    )
    row = cursor.fetchone()
    if row:
        datos["transporte_urbano"] = dict(row)

    cursor.execute("SELECT * FROM cultura WHERE localidad_id = ?", (localidad_id,))
    row = cursor.fetchone()
    if row:
        datos["cultura"] = dict(row)

    conn.close()
    return datos


def get_datos_comparativos(localidad_id: int) -> dict[str, Any]:
    """Obtiene datos comparativos (nacional, comunidad, provincia)."""
    conn = get_connection()
    cursor = conn.cursor()

    comparativos: dict[str, Any] = {}

    cursor.execute(
        """
        SELECT l.codigo_provincia, p.codigo_comunidad 
        FROM localidades l
        JOIN param_provincias p ON l.codigo_provincia = p.codigo_provincia
        WHERE l.id = ?
    """,
        (localidad_id,),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return comparativos

    codigo_provincia = row["codigo_provincia"]
    codigo_comunidad = row["codigo_comunidad"]

    cursor.execute("SELECT tipo, valor FROM datos_nacionales")
    datos_nacionales = {row["tipo"]: row["valor"] for row in cursor.fetchall()}
    comparativos["nacional"] = datos_nacionales

    cursor.execute(
        "SELECT tipo, valor FROM datos_comunidades WHERE codigo_comunidad = ?",
        (codigo_comunidad,),
    )
    datos_comunidad = {row["tipo"]: row["valor"] for row in cursor.fetchall()}
    comparativos["comunidad"] = datos_comunidad

    cursor.execute(
        "SELECT tipo, valor FROM datos_provincias WHERE codigo_provincia = ?",
        (codigo_provincia,),
    )
    datos_provincia = {row["tipo"]: row["valor"] for row in cursor.fetchall()}
    comparativos["provincia"] = datos_provincia

    conn.close()
    return comparativos


def calcular_puntuacion_100(puntuacion_raw: Optional[int]) -> int:
    """
    Transforma puntuación raw (rango -2 a 18) a escala 1-100.

    Usa interpolación lineal: ((score - min) / (max - min)) * 99 + 1
    """
    if puntuacion_raw is None:
        return 0

    # Interpolar de -2 a 18 -> 1 a 100
    score_range = SCORE_MAX - SCORE_MIN  # 20
    puntuacion_100 = ((puntuacion_raw - SCORE_MIN) / score_range) * 99 + 1

    return int(max(1, min(100, puntuacion_100)))


def get_color_categoria(categoria: Optional[str]) -> str:
    """Retorna color hex según categoría de calidad."""
    if categoria is None:
        return "#808080"

    cat_lower = categoria.lower()

    # Orden importante: primero los compuestos
    if "media-alta" in cat_lower:
        return "#32CD32"  # Verde claro (lime)
    elif "media-baja" in cat_lower:
        return "#FF8C00"  # Naranja
    elif "alta" in cat_lower and "media" not in cat_lower:
        return "#006400"  # Verde oscuro
    elif cat_lower == "media" or (
        cat_lower.startswith("media")
        and "alta" not in cat_lower
        and "baja" not in cat_lower
    ):
        return "#FFD700"  # Amarillo
    elif "baja" in cat_lower:
        return "#DC143C"  # Rojo

    return "#808080"
