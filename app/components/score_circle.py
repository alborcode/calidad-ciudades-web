# app/components/score_circle.py - Círculo de puntuación
"""
Componente de círculo de puntuación 1-100 con color según categoría.
"""

from nicegui import ui
from app.database import (
    get_color_categoria,
    calcular_puntuacion_100,
    get_categoria_from_score,
)


def crear_circulo_puntuacion(
    puntuacion_raw: int | None, categoria: str | None, tamano: str = "70px"
) -> ui.html:
    """
    Crea un círculo HTML con la puntuación 1-100 y color según categoría.

    La puntuación ya viene calculada desde nota_final de la BD.
    """
    puntuacion_100 = calcular_puntuacion_100(puntuacion_raw)

    # Calcular categoría basada en puntuación 100
    categoria_calc = get_categoria_from_score(puntuacion_100)
    color = get_color_categoria(categoria_calc)

    # SVG dimensions
    svg_size = 80
    radius = 30
    stroke_width = 8
    cx = svg_size // 2
    cy = svg_size // 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (puntuacion_100 / 100 * circumference)

    html = f'''
    <div style="
        width: {tamano};
        height: {tamano};
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <svg width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}" style="transform: rotate(-90deg);">
            <circle cx="{cx}" cy="{cy}" r="{radius}" 
                fill="none" stroke="#e0e0e0" stroke-width="{stroke_width}"/>
            <circle cx="{cx}" cy="{cy}" r="{radius}" 
                fill="none" stroke="{color}" stroke-width="{stroke_width}"
                stroke-linecap="round"
                stroke-dasharray="{circumference:.2f}"
                stroke-dashoffset="{offset:.2f}"/>
        </svg>
        <span style="
            position: absolute;
            font-size: 18px;
            font-weight: bold;
            color: {color};
        ">{puntuacion_100}</span>
    </div>
    '''

    return ui.html(html)


def crear_badge_categoria(categoria: str | None) -> ui.badge:
    """Crea un badge con el color de la categoría."""
    color = get_color_categoria(categoria)
    badge = ui.badge(categoria or "Sin datos", color=color, text_color="white").props(
        "rounded"
    )
    return badge
