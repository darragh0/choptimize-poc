from rich.console import Console

from choptimize.display.theme import APP_THEME

cout = Console(theme=APP_THEME)
cerr = Console(stderr=True, theme=APP_THEME)
