"""
ascii_play.resize


Frame downscaling with three quality levels.

  quality=1  nearest-neighbor  — fastest, aliased
  quality=2  4-tap supersample — smooth, near-zero extra cost (default)
  quality=3  full box filter   — true area average, best quality [depends but slows down. not feasible on loswer-end hardware or high fps vids ]
"""

import numpy as np


def resize_frame(frame: np.ndarray, out_h: int, out_w: int,
                 quality: int = 2) -> np.ndarray:
    """
    Resize (H, W, 3) uint8 frame to (out_h, out_w, 3).

    quality 1 — nearest-neighbor index sampling. Fast but shimmers on
                fine detail because it throws away inter-cell pixels.

    quality 2 — 4-tap box sample. Picks 4 source pixels spread across
                each output cell and averages them. Kills most aliasing
                at essentially no extra cost vs q1.

    quality 3 — Full box filter. Every source pixel votes into its
                destination cell. Identical to a proper video downscaler.
                Best for static images or when fps headroom exists.
    """
    h, w = frame.shape[:2]

    # ── quality 1: nearest-neighbor ──────────────────────────────────────────
    if quality == 1 or (out_h >= h and out_w >= w):
        ri = np.arange(out_h) * h // out_h
        ci = np.arange(out_w) * w // out_w
        return frame[np.ix_(ri, ci)]

    # ── quality 2: 4-tap supersample ─────────────────────────────────────────
    if quality == 2:
        def _c(idx, limit):
            return np.clip(idx, 0, limit - 1)

        ri0 = _c(np.arange(out_h) * h // out_h, h)
        ri1 = _c(ri0 + max(1, h // (2 * out_h)), h)
        ci0 = _c(np.arange(out_w) * w // out_w, w)
        ci1 = _c(ci0 + max(1, w // (2 * out_w)), w)

        s = (frame[np.ix_(ri0, ci0)].astype(np.uint16) +
             frame[np.ix_(ri0, ci1)].astype(np.uint16) +
             frame[np.ix_(ri1, ci0)].astype(np.uint16) +
             frame[np.ix_(ri1, ci1)].astype(np.uint16))
        return (s >> 2).astype(np.uint8)

    # ── quality 3: full box filter ────────────────────────────────────────────
    step_h = h / out_h
    step_w = w / out_w
    dst_rows = np.minimum((np.arange(h) / step_h).astype(np.int32), out_h - 1)
    dst_cols = np.minimum((np.arange(w) / step_w).astype(np.int32), out_w - 1)

    acc = np.zeros((out_h, out_w, 3), dtype=np.float32)
    cnt = np.zeros((out_h, out_w),    dtype=np.float32)
    for sr in range(h):
        dr = dst_rows[sr]
        np.add.at(acc[dr], dst_cols, frame[sr].astype(np.float32))
        np.add.at(cnt[dr], dst_cols, 1.0)

    return (acc / np.maximum(cnt, 1)[..., np.newaxis]).astype(np.uint8)
