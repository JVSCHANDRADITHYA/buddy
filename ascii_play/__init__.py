"""ascii_play — live terminal video player with true 24-bit color rendering."""

__version__ = "0.1.0"
__author__  = "your name"

from .player    import play
from .renderers import MODES

__all__ = ["play", "MODES", "__version__"]
