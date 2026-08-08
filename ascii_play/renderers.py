"""
ascii_play.renderers

Frame TO Ansi string renderers.

Each renderer signature:
    fn(frame: np.ndarray, cols: int, rows: int, quality: int) -> str

frame  : (H, W, 3) uint8 RGB
cols   : terminal columns to fill
rows   : terminal rows to fill
quality: 1-3 passed to resize_frame
"""

import numpy as np
from .ansi  import move_home, reset
from .resize import resize_frame

# ── Half-block ────────────────────────────────────────────────────────────────
#
# Uses U+2580 UPPER HALF BLOCK ▀
#   foreground color = top pixel row
#   background color = bottom pixel row
# → 2× effective vertical resolution per terminal row.

UPPER_HALF = "▀"

def render_half(frame: np.ndarray, cols: int, rows: int,
                quality: int = 2) -> str:
    """
    Best quality mode. Each terminal cell encodes two pixel rows via
    half-block character + 24-bit fg/bg color.
    """
    small = resize_frame(frame, rows * 2, cols, quality)  # (rows*2, cols, 3)
    top   = small[0::2]                                   # (rows,   cols, 3)
    bot   = small[1::2]                                   # (rows,   cols, 3)

    ft = top.reshape(-1, 3)
    fb = bot.reshape(-1, 3)

    _fg = np.frompyfunc(lambda r,g,b: f"\033[38;2;{r};{g};{b}m", 3, 1)
    _bg = np.frompyfunc(lambda r,g,b: f"\033[48;2;{r};{g};{b}m", 3, 1)

    fg = _fg(ft[:,0], ft[:,1], ft[:,2]).reshape(rows, cols)
    bg = _bg(fb[:,0], fb[:,1], fb[:,2]).reshape(rows, cols)

    cells = np.char.add(np.char.add(fg.astype(str), bg.astype(str)), UPPER_HALF)
    return move_home() + "\r\n".join("".join(row) for row in cells) + reset()


# ── ASCII density 

_ASCII_CHARS = np.array(list(" .:-=+*#%@"))

def render_ascii(frame: np.ndarray, cols: int, rows: int,
                 quality: int = 2) -> str:
    """
    Classic ASCII density chars with true 24-bit color per character.
    Lower spatial resolution than half-block but has the ASCII aesthetic.
    """
    small = resize_frame(frame, rows, cols, quality)      # (rows, cols, 3)

    gray = (small[...,0].astype(np.uint16) * 3 +
            small[...,1].astype(np.uint16) * 4 +
            small[...,2].astype(np.uint16)) >> 3          # (rows, cols)

    char_grid = _ASCII_CHARS[(gray * (len(_ASCII_CHARS) - 1) // 255)]

    flat = small.reshape(-1, 3)
    _fg  = np.frompyfunc(lambda r,g,b: f"\033[38;2;{r};{g};{b}m", 3, 1)
    fg   = _fg(flat[:,0], flat[:,1], flat[:,2]).reshape(rows, cols)

    cells = np.char.add(fg.astype(str), char_grid.astype(str))
    return move_home() + "\r\n".join("".join(row) for row in cells) + reset()


# ── Braille ───────────────────────────────────────────────────────────────────
#
# Each braille cell = 2 px wide × 4 px tall → 2× horiz + 4× vert resolution.
# Dot layout within a 2×4 pixel cell:
#   col 0  col 1
#   ●      ●     row 0  → bits 0x01, 0x08
#   ●      ●     row 1  → bits 0x02, 0x10
#   ●      ●     row 2  → bits 0x04, 0x20
#   ●      ●     row 3  → bits 0x40, 0x80

_BRAILLE_BASE = 0x2800
_BR_ROWS = np.array([0, 1, 2, 0, 3, 1, 2, 3])
_BR_COLS = np.array([0, 0, 0, 1, 0, 1, 1, 1])
_BR_BITS = np.array([0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80],
                    dtype=np.uint16)

def render_braille(frame: np.ndarray, cols: int, rows: int,
                   quality: int = 2) -> str:
    """
    Braille dot render. Highest spatial resolution of the three modes.
    Works best on high-contrast content.
    """
    small = resize_frame(frame, rows * 4, cols * 2, quality)  # (rows*4, cols*2, 3)

    gray  = (small[...,0].astype(np.uint16)*3 +
             small[...,1].astype(np.uint16)*4 +
             small[...,2].astype(np.uint16)) >> 3
    dots  = (gray > 64).astype(np.uint16)                 # (rows*4, cols*2)

    dcells = dots.reshape(rows, 4, cols, 2)               # (rows, 4, cols, 2)
    codes  = np.zeros((rows, cols), dtype=np.uint16)
    for i in range(8):
        codes += dcells[:, _BR_ROWS[i], :, _BR_COLS[i]] * _BR_BITS[i]
    codes += _BRAILLE_BASE

    chr_v     = np.frompyfunc(chr, 1, 1)
    char_grid = chr_v(codes.astype(int))

    colors = small.reshape(rows, 4, cols, 2, 3).mean(axis=(1,3)).astype(np.uint8)
    flat   = colors.reshape(-1, 3)
    _fg    = np.frompyfunc(lambda r,g,b: f"\033[38;2;{r};{g};{b}m", 3, 1)
    fg     = _fg(flat[:,0], flat[:,1], flat[:,2]).reshape(rows, cols)

    cells = np.char.add(fg.astype(str), char_grid.astype(str))
    return move_home() + "\r\n".join("".join(row) for row in cells) + reset()


# ── Registry ──────────────────────────────────────────────────────────────────

MODES = {
    "half":    render_half,
    "ascii":   render_ascii,
    "braille": render_braille,
}
