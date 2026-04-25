# app/main.py - Entry point
"""
Entry point de la aplicación Calidad Ciudades Web.
"""

from nicegui import ui
from app.pages.main_page import MainPage


# CSS responsivo para móvil
RESPONSIVE_CSS = """
/* Responsive: móviles (< 600px) */
@media (max-width: 599px) {
    /* Filtros: ancho completo en móvil */
    .filters-panel {
        width: 100% !important;
        min-width: 100% !important;
    }
    
    /* Resultados: ancho completo */
    .results-panel {
        width: 100% !important;
        min-width: 100% !important;
    }
    
    /* Diálogos: ancho casi completo */
    .q-dialog__inner--minimized {
        padding: 8px !important;
    }
    
    /* Tarjetas de resultados: más compactas */
    .q-card {
        padding: 12px !important;
    }
    
    /* Labels más pequeños */
    .text-h5, .text-h6 {
        font-size: 1.1em !important;
    }
    
    /* Grid de info: 2 columnas en móvil */
    .q-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}

/* Tablets (600px - 1024px) */
@media (min-width: 600px) and (max-width: 1023px) {
    .filters-panel {
        width: 280px !important;
        min-width: 280px !important;
    }
}

/* PC (> 1024px): comportamiento por defecto */
@media (min-width: 1024px) {
    .filters-panel {
        width: 320px !important;
    }
}

/* Ajustes globales */
.body--md {
    overflow-x: hidden;
}

/* Contenedor principal sin overflow */
.q-page {
    max-width: 100vw;
    overflow-x: hidden;
}
"""


@ui.page("/")
def main():
    """Página principal de la aplicación."""
    # Añadir CSS responsivo
    ui.add_css(RESPONSIVE_CSS)
    
    page = MainPage()
    page.build()


# Entry point directo
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Calidad de Ciudades",
        reload=True,
        port=8080,
        storage_secret="calidad-ciudades-secret-2024",
    )
