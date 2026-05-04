"""Étape 1 — Choix du produit avec filtre par audience."""

from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog
from typing import TYPE_CHECKING, List, Optional

import customtkinter as ctk

from .. import theme
from ..catalog import PRODUCTS, Product
from ..data import CustomEntry
from ..widgets.components import SelectableCard, make_ghost_button
from ..widgets.product_icons import get_icon_emoji, get_icon_image
from .base import WizardStep

if TYPE_CHECKING:
    from ..main import TriskellApp


# Filtre audience : (clé, label court chip, valeurs catalogue, couleur)
# Labels courts pour tenir sur une seule ligne même à la largeur min.
AUDIENCE_FILTERS: list[tuple[str, str, tuple[str, ...], str]] = [
    ("all",     "Tous",          ("B2B", "B2C", "Mixte", "Custom"), ""),
    ("pro",     "Pros",          ("B2B",),                          theme.TRISKELL_INDIGO),
    ("part",    "Particuliers",  ("B2C",),                          theme.TRISKELL_ORANGE),
    ("mixed",   "Mixtes",        ("Mixte",),                        theme.TRISKELL_VIOLET),
]


class StepProduct(WizardStep):
    """Liste des produits avec filtre audience + ajout manuel."""

    title = "On commence par quel produit ?"
    subtitle = "Choisis l'offre Triskell que tu vas pousser. Filtre par cible si tu veux aller plus vite."

    def __init__(self, parent: ctk.CTkFrame, app: "TriskellApp") -> None:
        super().__init__(parent, app)
        self._cards: List[SelectableCard] = []
        self._filter_buttons: List[ctk.CTkButton] = []
        self._active_filter: str = "all"

        # Header titre + sous-titre
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=theme.SPACE_2XL, pady=(theme.SPACE_LG, theme.SPACE_SM))

        ctk.CTkLabel(
            header,
            text=self.title,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TITLE, "bold"),
            text_color=app.colors.text_primary,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=self.subtitle,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            text_color=app.colors.text_secondary,
            anchor="w",
            justify="left",
            wraplength=820,
        ).pack(anchor="w", pady=(theme.SPACE_XS, 0))

        # Barre de filtres + bouton "Nouveau produit" sur la même ligne
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=theme.SPACE_2XL, pady=(theme.SPACE_MD, theme.SPACE_SM))

        # ---- Filtres pill (gauche) — tous les boutons sur une seule ligne ----
        filters_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filters_frame.pack(side="left")

        ctk.CTkLabel(
            filters_frame,
            text="Filtrer :",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
            text_color=app.colors.text_muted,
        ).pack(side="left", padx=(0, theme.SPACE_SM))

        for key, label, _audiences, swatch_color in AUDIENCE_FILTERS:
            btn = ctk.CTkButton(
                filters_frame,
                text=label,
                command=lambda k=key: self._set_filter(k),
                fg_color=app.colors.chip_bg,
                hover_color=app.colors.panel_hover,
                text_color=app.colors.text_secondary,
                border_width=1,
                border_color=app.colors.border,
                corner_radius=theme.RADIUS_PILL,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
                height=30,
                width=0,
            )
            btn.pack(side="left", padx=(0, 6), ipadx=8)
            btn._filter_key = key  # type: ignore[attr-defined]
            btn._swatch_color = swatch_color  # type: ignore[attr-defined]
            self._filter_buttons.append(btn)

        # ---- Bouton "Nouveau" compact (droite) ----
        self._add_btn = ctk.CTkButton(
            toolbar,
            text="✦  Nouveau",
            command=self._handle_add_custom,
            fg_color="transparent",
            hover_color=app.colors.panel_hover,
            text_color=app.colors.text_secondary,
            border_width=1,
            border_color=app.colors.border,
            corner_radius=theme.RADIUS_PILL,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
            height=30,
            width=0,
        )
        self._add_btn.pack(side="right", ipadx=10)

        # Zone scrollable des cards
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=app.colors.border,
            scrollbar_button_hover_color=app.colors.accent,
        )
        self._scroll.pack(
            fill="both",
            expand=True,
            padx=theme.SPACE_2XL,
            pady=(theme.SPACE_MD, theme.SPACE_LG),
        )

        self._refresh_filter_visuals()
        self._build_cards()

    # ------------------------------------------------------------------
    # Filtres
    # ------------------------------------------------------------------

    def _set_filter(self, key: str) -> None:
        self._active_filter = key
        self._refresh_filter_visuals()
        self._build_cards()

    def _refresh_filter_visuals(self) -> None:
        for btn in self._filter_buttons:
            key = getattr(btn, "_filter_key", "")
            swatch = getattr(btn, "_swatch_color", "")
            if key == self._active_filter:
                bg = swatch or self.app.colors.accent
                btn.configure(
                    fg_color=bg,
                    text_color="#FFFFFF",
                    border_color=bg,
                )
            else:
                btn.configure(
                    fg_color=self.app.colors.chip_bg,
                    text_color=self.app.colors.text_secondary,
                    border_color=self.app.colors.border,
                )

    def _audience_matches(self, audience: str) -> bool:
        for key, _label, audiences, _color in AUDIENCE_FILTERS:
            if key == self._active_filter:
                return audience in audiences
        return True

    # ------------------------------------------------------------------
    # Construction des cartes
    # ------------------------------------------------------------------

    def _build_cards(self) -> None:
        for w in self._scroll.winfo_children():
            w.destroy()
        self._cards = []

        self._scroll.grid_columnconfigure(0, weight=1, uniform="prod")
        self._scroll.grid_columnconfigure(1, weight=1, uniform="prod")

        all_entries: list[tuple[str, str, str, str]] = []
        for product in PRODUCTS:
            all_entries.append((product.key, product.label, product.tagline, product.audience))
        for entry in self.app.user_state.custom_products:
            all_entries.append((entry.key, entry.label, entry.description or "Produit personnalisé", "Custom"))

        # Application du filtre
        filtered = [e for e in all_entries if self._audience_matches(e[3])]

        if not filtered:
            ctk.CTkLabel(
                self._scroll,
                text="Aucun produit ne correspond à ce filtre.",
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
                text_color=self.app.colors.text_muted,
            ).grid(row=0, column=0, columnspan=2, pady=theme.SPACE_LG)
            return

        for idx, (key, label, desc, badge) in enumerate(filtered):
            icon_img = get_icon_image(key, size=44)
            icon_emoji = get_icon_emoji(key)
            card = SelectableCard(
                self._scroll,
                title=label,
                description=desc,
                value=key,
                colors=self.app.colors,
                on_click=self._handle_select,
                badge=badge,
                icon_image=icon_img,
                emoji=icon_emoji,
            )
            # sticky="new" : hauteur naturelle de la card (pas d'étirement vertical)
            card.grid(
                row=idx // 2,
                column=idx % 2,
                sticky="new",
                padx=(0 if idx % 2 == 0 else theme.SPACE_SM, theme.SPACE_SM if idx % 2 == 0 else 0),
                pady=(0, theme.SPACE_SM),
            )
            self._cards.append(card)

        # Réappliquer la sélection si la card sélectionnée est encore visible
        for card in self._cards:
            card.set_selected(card.value == self.app.session.product_key)

    # ------------------------------------------------------------------
    # Sélection produit
    # ------------------------------------------------------------------

    def _handle_select(self, value: str) -> None:
        self.app.session.product_key = value
        self.app.session.client_key = ""
        self.app.session.context_key = ""
        self.app.session.channel = ""
        for card in self._cards:
            card.set_selected(card.value == value)
        self.app.update_nav_state()

    def _handle_add_custom(self) -> None:
        label = simpledialog.askstring(
            "Nouveau produit",
            "Nom du produit personnalisé :",
            parent=self.app,
        )
        if not label:
            return
        label = label.strip()
        if not label:
            return
        description = simpledialog.askstring(
            "Description",
            "Décris brièvement ce produit (optionnel) :",
            parent=self.app,
        )
        key = "custom_" + "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
        existing_keys = {p.key for p in PRODUCTS} | {e.key for e in self.app.user_state.custom_products}
        original = key
        i = 2
        while key in existing_keys:
            key = f"{original}_{i}"
            i += 1
        self.app.user_state.custom_products.append(
            CustomEntry(key=key, label=label, description=(description or "").strip())
        )
        self.app.persist()
        self._build_cards()

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        for card in self._cards:
            card.set_selected(card.value == self.app.session.product_key)

    def is_valid(self) -> bool:
        return bool(self.app.session.product_key)
