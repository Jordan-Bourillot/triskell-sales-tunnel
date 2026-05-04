"""Composants UI réutilisables — cards, chips, boutons, toast.

Design Triskell : élévation au hover, glow turquoise sur l'actif, indicateurs
visuels (barre latérale + check) sur la sélection.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional

import customtkinter as ctk

from .. import theme


# ---------------------------------------------------------------------------
# Carte sélectionnable (produit / client)
# ---------------------------------------------------------------------------

class SelectableCard(ctk.CTkFrame):
    """Carte cliquable avec titre + description + chip de priorité optionnel.

    États : default → hover → selected. La sélection ajoute :
    - bordure accent
    - barre verticale turquoise à gauche (indicateur visuel)
    - check ✓ à droite
    """

    # Mapping audience -> (label court, couleur fond, couleur texte)
    # Labels courts pour pills discrètes ; détail audience dans les filtres et titres.
    AUDIENCE_STYLES: dict[str, tuple[str, str, str]] = {
        "B2B":     ("Pros",        theme.TRISKELL_INDIGO, "#FFFFFF"),
        "B2C":     ("Particuliers", theme.TRISKELL_ORANGE, "#1A0A02"),
        "Mixte":   ("Mixte",       theme.TRISKELL_VIOLET, "#FFFFFF"),
        "Custom":  ("Custom",      theme.D_GOLD,          "#1A1208"),
    }

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        description: str,
        value: str,
        colors: theme.ThemeColors,
        on_click: Callable[[str], None],
        priority: Optional[int] = None,
        badge: Optional[str] = None,
        emoji: Optional[str] = None,
        icon_image: Optional["ctk.CTkImage"] = None,
    ) -> None:
        # Hauteur fixe (avec grid_propagate False) → toutes les cards alignées
        # à la même hauteur compacte, peu importe l'espace dispo dans le scroll.
        super().__init__(
            parent,
            fg_color=colors.panel,
            corner_radius=theme.RADIUS_MD,
            border_width=1,
            border_color=colors.border,
            height=92,
        )
        self.grid_propagate(False)
        self._value = value
        self._colors = colors
        self._on_click = on_click
        self._selected = False

        # Layout compact : [sidebar 3px][icon 56px][content stretch]
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barre latérale gauche (indicateur de sélection)
        self._side_bar = ctk.CTkFrame(
            self,
            fg_color=colors.panel,
            width=3,
            corner_radius=0,
        )
        self._side_bar.grid(row=0, column=0, sticky="ns")

        # Icône produit (image ou emoji) — colonne 1
        icon_size = 48
        icon_frame = ctk.CTkFrame(
            self,
            fg_color=colors.panel_elevated,
            corner_radius=theme.RADIUS_SM,
            width=icon_size,
            height=icon_size,
        )
        icon_frame.grid(row=0, column=1, sticky="n", padx=(theme.SPACE_MD, theme.SPACE_MD), pady=theme.SPACE_MD)
        icon_frame.grid_propagate(False)
        icon_frame.grid_rowconfigure(0, weight=1)
        icon_frame.grid_columnconfigure(0, weight=1)

        if icon_image is not None:
            self._icon = ctk.CTkLabel(icon_frame, text="", image=icon_image)
        else:
            self._icon = ctk.CTkLabel(
                icon_frame,
                text=emoji or "✦",
                font=(theme.FONT_FAMILY, 22),
                text_color=colors.accent,
            )
        self._icon.grid(row=0, column=0, sticky="nsew")

        # Contenu (titre + badge + desc) — colonne 2
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=2, sticky="nsew", padx=(0, theme.SPACE_MD), pady=theme.SPACE_MD)
        content.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(content, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        self._title = ctk.CTkLabel(
            title_row,
            text=title,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY_LG, "bold"),
            text_color=colors.text_primary,
            anchor="w",
            justify="left",
        )
        self._title.grid(row=0, column=0, sticky="w")

        # Badge / priority chip (à droite du titre)
        right_zone = ctk.CTkFrame(title_row, fg_color="transparent")
        right_zone.grid(row=0, column=1, sticky="e", padx=(theme.SPACE_SM, 0))

        if priority is not None:
            self._build_priority_chip(right_zone, priority).pack(side="left", padx=(0, theme.SPACE_XS))

        if badge:
            audience_label, audience_bg, audience_fg = self.AUDIENCE_STYLES.get(
                badge,
                (badge, colors.panel_elevated, colors.text_primary),
            )
            self._badge = ctk.CTkLabel(
                right_zone,
                text=audience_label,
                font=(theme.FONT_FAMILY, 9, "bold"),
                text_color=audience_fg,
                fg_color=audience_bg,
                corner_radius=theme.RADIUS_PILL,
                padx=7,
                pady=1,
                height=18,
            )
            self._badge.pack(side="left")

        # Check ✓ — visible uniquement quand sélectionné (overlay coin haut-droit)
        self._check = ctk.CTkLabel(
            right_zone,
            text="",
            font=(theme.FONT_FAMILY, 13, "bold"),
            text_color=colors.accent,
        )
        self._check.pack(side="left", padx=(theme.SPACE_XS, 0))

        # Description compacte (1-2 lignes max via wraplength)
        self._desc = ctk.CTkLabel(
            content,
            text=description,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
            text_color=colors.text_secondary,
            anchor="w",
            justify="left",
            wraplength=380,
        )
        self._desc.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Bind click
        for w in self._widgets_for_binding():
            w.bind("<Button-1>", self._handle_click)
            w.bind("<Enter>", self._handle_enter)
            w.bind("<Leave>", self._handle_leave)
            w.configure(cursor="hand2")
        self._icon.bind("<Button-1>", self._handle_click)
        self._icon.bind("<Enter>", self._handle_enter)
        self._icon.bind("<Leave>", self._handle_leave)
        self._icon.configure(cursor="hand2")
        icon_frame.bind("<Button-1>", self._handle_click)
        icon_frame.configure(cursor="hand2")

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._refresh_appearance()

    @property
    def value(self) -> str:
        return self._value

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _widgets_for_binding(self) -> List[tk.Widget]:
        return [self, self._title, self._desc]

    def _build_priority_chip(self, parent: tk.Widget, priority: int) -> ctk.CTkLabel:
        # Labels courts (★ = haute, ●● = moyenne, ● = standard) pour pill discrète.
        labels = {1: "★ Haute", 2: "● Moyenne", 3: "Standard"}
        label = labels.get(priority, "Priorité")
        bg = {
            1: self._colors.accent,
            2: theme.WARNING,
            3: self._colors.text_muted,
        }.get(priority, self._colors.border)
        fg = self._colors.accent_text if priority == 1 else "#08121A"
        return ctk.CTkLabel(
            parent,
            text=label,
            font=(theme.FONT_FAMILY, 9, "bold"),
            text_color=fg,
            fg_color=bg,
            corner_radius=theme.RADIUS_PILL,
            padx=7,
            pady=1,
            height=18,
        )

    def _handle_click(self, _event: tk.Event) -> None:
        self._on_click(self._value)

    def _handle_enter(self, _event: tk.Event) -> None:
        if not self._selected:
            self.configure(fg_color=self._colors.panel_hover, border_color=self._colors.accent)

    def _handle_leave(self, _event: tk.Event) -> None:
        self._refresh_appearance()

    def _refresh_appearance(self) -> None:
        if self._selected:
            self.configure(
                fg_color=self._colors.panel_elevated,
                border_color=self._colors.accent,
                border_width=2,
            )
            self._side_bar.configure(fg_color=self._colors.accent)
            self._check.configure(text="✓")
        else:
            self.configure(
                fg_color=self._colors.panel,
                border_color=self._colors.border,
                border_width=1,
            )
            self._side_bar.configure(fg_color=self._colors.panel)
            self._check.configure(text="")


# ---------------------------------------------------------------------------
# Chip canal
# ---------------------------------------------------------------------------

class ChannelChip(ctk.CTkFrame):
    """Carte chip pour un canal (Email / LinkedIn / etc.) — taille L, sélectionnable."""

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        icon: str,
        value: str,
        colors: theme.ThemeColors,
        on_click: Callable[[str], None],
        recommended: bool = False,
    ) -> None:
        super().__init__(
            parent,
            fg_color=colors.chip_bg,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=colors.border,
            width=170,
            height=110,
        )
        self.grid_propagate(False)
        self._value = value
        self._colors = colors
        self._on_click = on_click
        self._selected = False
        self._recommended = recommended

        self._icon = ctk.CTkLabel(
            self,
            text=icon,
            font=(theme.FONT_FAMILY, 26, "bold"),
            text_color=colors.accent,
        )
        self._icon.pack(pady=(theme.SPACE_LG, 0))

        self._label = ctk.CTkLabel(
            self,
            text=label,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY_LG, "bold"),
            text_color=colors.chip_text,
        )
        self._label.pack(pady=(theme.SPACE_XS, 0))

        if recommended:
            self._reco = ctk.CTkLabel(
                self,
                text="★ Optimisé",
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_TINY, "bold"),
                text_color=colors.accent,
                fg_color="transparent",
            )
            self._reco.pack(pady=(2, theme.SPACE_SM))
        else:
            self._reco = None
            ctk.CTkLabel(self, text=" ", font=(theme.FONT_FAMILY, theme.FONT_SIZE_TINY)).pack(pady=(2, theme.SPACE_SM))

        for w in (self, self._icon, self._label):
            w.bind("<Button-1>", self._handle_click)
            w.bind("<Enter>", self._handle_enter)
            w.bind("<Leave>", self._handle_leave)
            w.configure(cursor="hand2")
        if self._reco:
            self._reco.bind("<Button-1>", self._handle_click)
            self._reco.configure(cursor="hand2")

    @property
    def value(self) -> str:
        return self._value

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._refresh_appearance()

    def _handle_click(self, _event: tk.Event) -> None:
        self._on_click(self._value)

    def _handle_enter(self, _event: tk.Event) -> None:
        if not self._selected:
            self.configure(fg_color=self._colors.panel_hover, border_color=self._colors.accent)

    def _handle_leave(self, _event: tk.Event) -> None:
        self._refresh_appearance()

    def _refresh_appearance(self) -> None:
        if self._selected:
            self.configure(
                fg_color=self._colors.chip_active_bg,
                border_color=self._colors.accent,
                border_width=2,
            )
            self._label.configure(text_color=self._colors.chip_active_text)
            self._icon.configure(text_color=self._colors.chip_active_text)
            if self._reco:
                self._reco.configure(text_color=self._colors.chip_active_text)
        else:
            self.configure(
                fg_color=self._colors.chip_bg,
                border_color=self._colors.border,
                border_width=1,
            )
            self._label.configure(text_color=self._colors.chip_text)
            self._icon.configure(text_color=self._colors.accent)
            if self._reco:
                self._reco.configure(text_color=self._colors.accent)


# ---------------------------------------------------------------------------
# Boutons stylés
# ---------------------------------------------------------------------------

def make_primary_button(
    parent: tk.Widget,
    text: str,
    command: Callable[[], None],
    colors: theme.ThemeColors,
    width: int = 180,
    height: int = 44,
) -> ctk.CTkButton:
    # DECISION: Tk ne sait pas faire de vrai gradient sur un bouton. On approxime
    # le gradient site officiel (indigo → violet) en utilisant indigo en
    # base et violet au hover. Le ressenti reste très "Triskell".
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=colors.accent,
        hover_color=colors.accent_secondary,
        text_color=colors.accent_text,
        font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY_LG, "bold"),
        corner_radius=theme.RADIUS_PILL,
        height=height,
        width=width,
    )


def make_ghost_button(
    parent: tk.Widget,
    text: str,
    command: Callable[[], None],
    colors: theme.ThemeColors,
    width: int = 140,
    height: int = 42,
) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="transparent",
        hover_color=colors.panel_hover,
        text_color=colors.text_secondary,
        font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
        corner_radius=theme.RADIUS_PILL,
        border_width=1,
        border_color=colors.border,
        height=height,
        width=width,
    )


def make_subtle_button(
    parent: tk.Widget,
    text: str,
    command: Callable[[], None],
    colors: theme.ThemeColors,
    width: int = 130,
) -> ctk.CTkButton:
    """Bouton plat sans bordure (pour actions secondaires header / footer)."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="transparent",
        hover_color=colors.panel_hover,
        text_color=colors.text_secondary,
        font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
        corner_radius=theme.RADIUS_PILL,
        border_width=1,
        border_color=colors.border,
        height=32,
        width=width,
    )


# ---------------------------------------------------------------------------
# Toast — notification éphémère
# ---------------------------------------------------------------------------

class Toast(ctk.CTkFrame):
    """Notification flottante en bas d'un parent. Auto-dismiss configurable."""

    def __init__(
        self,
        parent: tk.Widget,
        message: str,
        colors: theme.ThemeColors,
        kind: str = "success",  # success | info | error
        duration_ms: int = 2400,
    ) -> None:
        bg = {
            "success": colors.success,
            "info": colors.accent,
            "error": colors.danger,
        }.get(kind, colors.accent)
        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=theme.RADIUS_PILL,
            height=42,
        )
        self._duration_ms = duration_ms

        icon = {"success": "✓", "info": "ℹ", "error": "⚠"}.get(kind, "•")
        ctk.CTkLabel(
            self,
            text=f"  {icon}  {message}  ",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY, "bold"),
            text_color=colors.toast_text if kind != "success" else "#04211F",
        ).pack(padx=theme.SPACE_LG, pady=theme.SPACE_SM)

        self.place(relx=0.5, rely=0.96, anchor="s")
        self.after(duration_ms, self.destroy)
