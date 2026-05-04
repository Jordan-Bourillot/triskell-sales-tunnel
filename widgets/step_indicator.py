"""Indicateur de progression du tunnel (4 étapes).

Design Triskell : barre continue avec gradient progressif simulé,
cercles avec glow sur l'étape active, labels typés.
"""

from __future__ import annotations

import tkinter as tk
from typing import List

import customtkinter as ctk

from .. import theme


class StepIndicator(ctk.CTkFrame):
    """Barre horizontale de 4 étapes avec progression visuelle."""

    def __init__(
        self,
        parent: tk.Widget,
        steps: List[str],
        colors: theme.ThemeColors,
        height: int = 84,
    ) -> None:
        super().__init__(parent, fg_color="transparent", height=height)
        self._steps = steps
        self._current = 0
        self._colors = colors

        self._canvas = tk.Canvas(
            self,
            bg=self._colors.bg,
            highlightthickness=0,
            height=height,
        )
        self._canvas.pack(fill="both", expand=True, padx=theme.SPACE_2XL, pady=(theme.SPACE_MD, 0))
        self._canvas.bind("<Configure>", lambda _e: self._render())

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def set_step(self, index: int) -> None:
        self._current = max(0, min(len(self._steps) - 1, index))
        self._render()

    def update_colors(self, colors: theme.ThemeColors) -> None:
        self._colors = colors
        self._canvas.configure(bg=colors.bg)
        self._render()

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def _render(self) -> None:
        c = self._canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            return

        n = len(self._steps)
        if n < 2:
            return

        radius_outer = 22
        radius_inner = 16
        margin = 70
        usable = max(1, w - margin * 2)
        gap = usable / (n - 1)
        line_y = 30

        # 1. Lignes reliantes (background)
        for i in range(n - 1):
            x1 = margin + i * gap
            x2 = margin + (i + 1) * gap
            c.create_line(
                x1, line_y, x2, line_y,
                fill=self._colors.border,
                width=4,
                capstyle="round",
            )

        # 2. Lignes "complétées" par-dessus (accent)
        for i in range(self._current):
            x1 = margin + i * gap
            x2 = margin + (i + 1) * gap
            c.create_line(
                x1, line_y, x2, line_y,
                fill=self._colors.accent,
                width=4,
                capstyle="round",
            )

        # 3. Cercles + labels
        for i, label in enumerate(self._steps):
            cx = margin + i * gap
            cy = line_y
            done = i < self._current
            current = i == self._current

            # Glow autour du cercle actif
            if current:
                glow_r = radius_outer + 8
                c.create_oval(
                    cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                    outline=self._colors.accent_glow,
                    width=2,
                    stipple="gray25",
                )

            if done:
                fill, outline, num_color = (
                    self._colors.accent, self._colors.accent, self._colors.accent_text,
                )
                num = "✓"
            elif current:
                fill, outline, num_color = (
                    self._colors.bg_alt, self._colors.accent, self._colors.accent,
                )
                num = str(i + 1)
            else:
                fill, outline, num_color = (
                    self._colors.bg_alt, self._colors.border, self._colors.text_muted,
                )
                num = str(i + 1)

            r = radius_outer if current else radius_inner
            c.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=fill, outline=outline, width=2 if current else 1.5,
            )
            c.create_text(
                cx, cy,
                text=num,
                fill=num_color,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_HEADING, "bold"),
            )

            # Label sous le cercle
            text_color = self._colors.text_primary if (current or done) else self._colors.text_muted
            weight = "bold" if current else "normal"
            c.create_text(
                cx, cy + radius_outer + 16,
                text=label,
                fill=text_color,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, weight),
            )
