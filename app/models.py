# app/models.py - Modelos de datos
"""
Modelos de datos para la aplicación Calidad Ciudades.
Contiene tipos y dataclasses adicionales.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LocalidadDetalle:
    """Detalle completo de una localidad para el diálogo."""

    id: int
    nombre: str
    provincia: str
    comunidad: str
    poblacion: Optional[int]
    latitud: Optional[float]
    longitud: Optional[float]
    altitud: Optional[float]
    puntuacion: Optional[int]
    categoria: Optional[str]
    puntuacion_100: int
    color_categoria: str
    wikipedia_url: str
    datos: dict
    comparativos: dict
