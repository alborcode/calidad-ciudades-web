# app/utils/geo.py - utilidades geográficas
"""
Funciones geográficas pequeñas y puras.
"""
from math import radians, sin, cos, sqrt, atan2


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia en kilómetros entre dos puntos GPS usando la fórmula de Haversine.

    Se aplica un factor de corrección (1.25) para aproximar distancia por carretera,
    ya que las coordenadas de la BD son de sedes administrativas, no del centroide exacto.

    Retorna la distancia en kilómetros (float).
    """
    # Validar entradas
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0

    # Radio de la Tierra en km
    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    # Factor de corrección para aproximar distancia por carretera
    FACTOR_CORRECCION = 1.25
    return round(distance * FACTOR_CORRECCION, 1)
