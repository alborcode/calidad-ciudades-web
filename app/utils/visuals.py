"""
app/utils/visuals.py

Helpers para normalizar la visualización comparativa frente a medias nacionales.

Principios:
- Funciones puras y pequeñas (fácil de testear).
- Documentación breve en español (proyecto usa español para docs).
"""
from typing import Optional, Tuple


def compare_to_national(
    value: Optional[float],
    national: Optional[float],
    better_when_higher: bool = True,
    thresholds: Tuple[float, float] = (0.9, 1.1),
    tokens: Tuple[str, str, str] = ("green-7", "orange-7", "red-7"),
) -> Optional[str]:
    """
    Compara un valor local con su media nacional y devuelve un token de color.

    - value: valor local (por ejemplo tasa, renta, precio)
    - national: valor de referencia nacional
    - better_when_higher: True si un valor mayor es mejor (ej. renta), False si menor es mejor (ej. paro)
    - thresholds: (low, high) umbrales aplicados sobre la _ratio_ local/nacional
        Ejemplo: (0.9, 1.1) ->
          - si better_when_higher: ratio >= 1.1 => verde, >= 0.9 => naranja, else rojo
          - si not better_when_higher: ratio <= 0.9 => verde, <= 1.1 => naranja, else rojo
    - tokens: triple (verde, naranja, rojo) retornado según resultado

    Retorna: token de color (string) o None si no hay datos válidos.
    """

    # Validación básica
    if value is None or national is None:
        return None

    try:
        # Evitar división por cero
        if national == 0:
            return None

        ratio = float(value) / float(national)
    except Exception:
        return None

    low, high = thresholds
    green, orange, red = tokens

    if better_when_higher:
        if ratio >= high:
            return green
        elif ratio >= low:
            return orange
        else:
            return red
    else:
        if ratio <= low:
            return green
        elif ratio <= high:
            return orange
        else:
            return red


def token_to_quasar_color(token: Optional[str]) -> Optional[str]:
    """
    Normaliza un token de color a la forma que NiceGUI/Quasar espera.

    Actualmente los tokens se pasan directamente a NiceGUI (por ejemplo "green-7").
    Esta función actúa como adaptador futuro y devuelve el mismo token si está presente.
    """
    return token
