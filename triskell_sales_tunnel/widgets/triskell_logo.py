"""Logo Triskell officiel — 3 feuilles spiralées indigo / violet / orange.

Reproduction fidèle de `og-image.svg` du site officiel triskell-studio.fr :
- Feuille 1 : Indigo  #6366F1 (angle 0°)
- Feuille 2 : Violet  #8B5CF6 (rotation 120°)
- Feuille 3 : Orange  #F97316 (rotation 240°)
- Centre   : disque sombre
- Path SVG source : M18,18 C20,15 22,10 20,6 C18,2 13,3 13,7.5 C13,12 16,15.5 18,18Z

DECISION: chaque feuille est rendue via `create_polygon(smooth=True)` à partir
de points clés extraits de la courbe Bézier — Tk Canvas ne supporte pas les
courbes de Bézier natives mais les polygones lissés s'en rapprochent.
"""

from __future__ import annotations

import math
import tkinter as tk
from typing import List, Tuple

import customtkinter as ctk


# Couleurs officielles (correspondent à og-image.svg + Table Ronde)
COLOR_LEAF_1 = "#6366F1"  # indigo
COLOR_LEAF_2 = "#A78BFA"  # violet (Table Ronde, plus chaud)
COLOR_LEAF_3 = "#F97316"  # orange
COLOR_CENTER = "#0F1218"  # gris bleuté Table Ronde
COLOR_GLOW = "#A78BFA"    # halo violet
COLOR_GOLD = "#D4B35A"    # halo or signature Table Ronde


# Points clés de la feuille SVG, normalisés dans une bbox 36×36 centrée sur (18, 18).
# Reproduction approximative de :
# M18,18 C20,15 22,10 20,6 C18,2 13,3 13,7.5 C13,12 16,15.5 18,18 Z
# Densifiée pour smoothing Tk.
_LEAF_POINTS_NORMALIZED: List[Tuple[float, float]] = [
    (18.0, 18.0),
    (19.0, 16.5),
    (20.0, 15.0),
    (21.0, 12.5),
    (22.0, 10.0),
    (21.5, 8.0),
    (20.0, 6.0),
    (18.5, 4.0),
    (16.0, 3.0),
    (14.0, 3.5),
    (13.0, 5.0),
    (13.0, 7.5),
    (13.5, 10.0),
    (14.5, 12.0),
    (16.0, 14.0),
    (17.0, 16.0),
    (18.0, 18.0),
]


class TriskellLogo(ctk.CTkCanvas):
    """Logo officiel Triskell : 3 feuilles spiralées."""

    def __init__(
        self,
        parent: tk.Widget,
        size: int = 56,
        bg: str = COLOR_CENTER,
        leaf_indigo: str = COLOR_LEAF_1,
        leaf_violet: str = COLOR_LEAF_2,
        leaf_orange: str = COLOR_LEAF_3,
        center: str = COLOR_CENTER,
        glow: str = COLOR_GLOW,
        gold: str = COLOR_GOLD,
        # Compat ascendante avec l'ancienne signature
        color: str | None = None,
        accent: str | None = None,
    ) -> None:
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg,
            highlightthickness=0,
            borderwidth=0,
        )
        self._size = size
        self._bg = bg
        self._leaf_1 = leaf_indigo
        self._leaf_2 = leaf_violet
        self._leaf_3 = leaf_orange
        self._center = center
        self._glow = glow
        self._gold = gold
        self._draw()

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def set_bg(self, bg: str) -> None:
        self._bg = bg
        self.configure(bg=bg)
        self.delete("all")
        self._draw()

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        s = self._size
        cx, cy = s / 2, s / 2

        # Halo violet doux derrière
        self._draw_halo(cx, cy, s)

        # 3 feuilles à 0°, 120°, 240°
        leaf_colors = (self._leaf_1, self._leaf_2, self._leaf_3)
        for i, color in enumerate(leaf_colors):
            angle = i * 120
            self._draw_leaf(cx, cy, s, angle, color)

        # Disque central
        center_r = max(2, s * 0.075)
        self.create_oval(
            cx - center_r, cy - center_r, cx + center_r, cy + center_r,
            fill=self._center, outline="",
        )

    def _draw_halo(self, cx: float, cy: float, s: float) -> None:
        # Halo or extérieur (signature Table Ronde) puis halo violet plus serré.
        for factor, stipple, color in (
            (0.66, "gray12", self._gold),
            (0.60, "gray25", self._gold),
            (0.54, "gray50", self._glow),
            (0.48, "gray75", self._glow),
        ):
            r = s * factor
            self.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=color,
                width=max(1, s // 60),
                stipple=stipple,
            )

    def _draw_leaf(
        self,
        cx: float,
        cy: float,
        size: float,
        rotate_deg: float,
        color: str,
    ) -> None:
        """Trace une feuille à partir des points normalisés, rotée et centrée."""

        # Échelle : la bbox normalisée fait 36 unités, on veut occuper ~75% du logo
        target_extent = size * 0.78
        scale = target_extent / 36.0

        # Centre de rotation = (18, 18) en coordonnées normalisées,
        # qui correspond au centre du logo (cx, cy).
        rad = math.radians(rotate_deg)
        cos_t = math.cos(rad)
        sin_t = math.sin(rad)

        flat_coords: List[float] = []
        for (nx, ny) in _LEAF_POINTS_NORMALIZED:
            # Translation pour centrer sur (18,18) puis scale, puis rotation, puis re-translation au centre canvas
            ox = (nx - 18.0) * scale
            oy = (ny - 18.0) * scale
            rx = ox * cos_t - oy * sin_t
            ry = ox * sin_t + oy * cos_t
            flat_coords.append(cx + rx)
            flat_coords.append(cy + ry)

        # Polygon avec smoothing pour adoucir la courbe.
        self.create_polygon(
            *flat_coords,
            fill=color,
            outline="",
            smooth=True,
            splinesteps=18,
        )
