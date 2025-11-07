"""Display theme configuration for choptimize.

Defines semantic color scheme and UI elements following accessibility best practices.
"""

from rich.theme import Theme

# Application color theme (WCAG 2.1 compliant, colorblind-safe)
APP_THEME = Theme({
    # Headings
    "heading.primary": "bold bright_blue",
    "heading.secondary": "bold cyan",

    # Status indicators
    "status.info": "bright_cyan",
    "status.success": "bright_green",
    "status.warning": "bright_yellow",
    "status.error": "bright_red",

    # Metric scores
    "score.excellent": "bold bright_green",   # 9-10
    "score.good": "bold green",               # 7-8
    "score.fair": "bold bright_yellow",       # 5-6
    "score.poor": "bold yellow",              # 3-4
    "score.very_poor": "bold bright_red",     # 1-2

    # UI elements
    "border.default": "bright_black",
    "border.accent": "bright_blue",
    "border.success": "bright_green",
    "label": "cyan",
    "value": "white",
    "emphasis": "bold",

    # Table styles
    "table.header": "bold bright_blue",
    "table.row": "white",
})

# Section icons for visual scanning
ICONS = {
    "prompt": "📝",
    "analysis": "📊",
    "assessment": "💭",
    "recommendations": "💡",
    "improved": "✨",
}
