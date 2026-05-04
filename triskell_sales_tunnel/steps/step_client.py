"""Étape 2 — Choix du client cible + situation/contexte."""

from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog
from typing import TYPE_CHECKING, List

import customtkinter as ctk

from .. import theme
from ..catalog import get_product
from ..data import CustomEntry
from ..widgets.components import SelectableCard, make_ghost_button
from .base import WizardStep

if TYPE_CHECKING:
    from ..main import TriskellApp


class StepClient(WizardStep):
    """Suggestions de cibles classées par priorité, selon le produit + situation."""

    title = "C'est qui qu'on cible ?"
    subtitle = "Suggestions priorisées selon le produit. Précise aussi la situation pour adapter le message."

    def __init__(self, parent: ctk.CTkFrame, app: "TriskellApp") -> None:
        super().__init__(parent, app)
        self._cards: List[SelectableCard] = []

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=theme.SPACE_2XL, pady=(theme.SPACE_LG, theme.SPACE_SM))

        self._title_label = ctk.CTkLabel(
            header,
            text=self.title,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TITLE, "bold"),
            text_color=app.colors.text_primary,
            anchor="w",
        )
        self._title_label.pack(anchor="w")

        self._subtitle_label = ctk.CTkLabel(
            header,
            text=self.subtitle,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            text_color=app.colors.text_secondary,
            anchor="w",
            justify="left",
            wraplength=820,
        )
        self._subtitle_label.pack(anchor="w", pady=(theme.SPACE_XS, 0))

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=theme.SPACE_2XL, pady=(theme.SPACE_MD, theme.SPACE_SM))
        ctk.CTkButton(
            toolbar,
            text="✦  Nouvelle cible",
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
        ).pack(side="left", ipadx=10)

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
            pady=(theme.SPACE_MD, theme.SPACE_SM),
        )

        # ----- Bandeau "Situation" (contextes) en bas — visible si le produit en a -----
        self._context_zone = ctk.CTkFrame(self, fg_color=app.colors.bg_alt, corner_radius=0)
        self._context_zone.pack(fill="x", side="bottom")

        self._context_label = ctk.CTkLabel(
            self._context_zone,
            text="Situation du prospect",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
            text_color=app.colors.gold,
            anchor="w",
        )
        self._context_label.pack(anchor="w", padx=theme.SPACE_2XL, pady=(theme.SPACE_MD, 4))

        self._context_chips_row = ctk.CTkFrame(self._context_zone, fg_color="transparent")
        self._context_chips_row.pack(anchor="w", padx=theme.SPACE_2XL, pady=(0, theme.SPACE_MD))

        self._context_buttons: List[ctk.CTkButton] = []

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_cards(self) -> None:
        for w in self._scroll.winfo_children():
            w.destroy()
        self._cards = []

        product_key = self.app.session.product_key
        product = get_product(product_key)

        # Construire la liste avant placement, pour la mise en grille
        entries: list[tuple[str, str, str, int | None, str | None]] = []
        if product:
            for client in sorted(product.clients, key=lambda c: c.priority):
                entries.append((client.key, client.label, client.description, client.priority, None))
        for entry in self.app.user_state.custom_clients:
            if entry.parent_product_key and entry.parent_product_key != product_key:
                continue
            entries.append((entry.key, entry.label, entry.description or "Cible personnalisée", None, "Custom"))

        if not entries:
            ctk.CTkLabel(
                self._scroll,
                text=(
                    "Ce produit personnalisé n'a pas de cibles pré-suggérées. "
                    "Ajoute la tienne en haut à gauche."
                ),
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
                text_color=self.app.colors.text_muted,
                wraplength=820,
                justify="left",
            ).pack(anchor="w", pady=theme.SPACE_LG)
            return

        # Grille 2 colonnes
        self._scroll.grid_columnconfigure(0, weight=1, uniform="cli")
        self._scroll.grid_columnconfigure(1, weight=1, uniform="cli")

        for idx, (key, label, desc, priority, badge) in enumerate(entries):
            card = SelectableCard(
                self._scroll,
                title=label,
                description=desc,
                value=key,
                colors=self.app.colors,
                on_click=self._handle_select,
                priority=priority,
                badge=badge,
            )
            # sticky="new" : hauteur naturelle (pas d'étirement vertical par la grid)
            card.grid(
                row=idx // 2,
                column=idx % 2,
                sticky="new",
                padx=(0 if idx % 2 == 0 else theme.SPACE_SM, theme.SPACE_SM if idx % 2 == 0 else 0),
                pady=(0, theme.SPACE_SM),
            )
            self._cards.append(card)

    # ------------------------------------------------------------------
    # Sélection
    # ------------------------------------------------------------------

    def _handle_select(self, value: str) -> None:
        self.app.session.client_key = value
        self.app.session.channel = ""
        for card in self._cards:
            card.set_selected(card.value == value)
        self.app.update_nav_state()

    # ------------------------------------------------------------------
    # Contextes (situation prospect)
    # ------------------------------------------------------------------

    def _build_contexts(self) -> None:
        for w in self._context_chips_row.winfo_children():
            w.destroy()
        self._context_buttons = []

        product = get_product(self.app.session.product_key)
        contexts = product.contexts if product else ()

        if not contexts:
            self._context_zone.pack_forget()
            return
        self._context_zone.pack(fill="x", side="bottom")

        # Chip "Sans précision" toujours présent + chips spécifiques
        all_options = (("", "Sans précision"),) + tuple((c.key, c.label) for c in contexts)

        for key, label in all_options:
            btn = ctk.CTkButton(
                self._context_chips_row,
                text=label,
                command=lambda k=key: self._handle_context(k),
                fg_color=self.app.colors.chip_bg,
                hover_color=self.app.colors.panel_hover,
                text_color=self.app.colors.text_secondary,
                border_width=1,
                border_color=self.app.colors.border,
                corner_radius=theme.RADIUS_PILL,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
                height=30,
                width=0,  # auto
            )
            btn.pack(side="left", padx=(0, theme.SPACE_SM))
            self._context_buttons.append(btn)
            btn._ctx_key = key  # type: ignore[attr-defined]

        self._refresh_context_visuals()

    def _handle_context(self, key: str) -> None:
        self.app.session.context_key = key
        self._refresh_context_visuals()

    def _refresh_context_visuals(self) -> None:
        active = self.app.session.context_key
        for btn in self._context_buttons:
            key = getattr(btn, "_ctx_key", "")
            if key == active:
                btn.configure(
                    fg_color=self.app.colors.accent,
                    text_color=self.app.colors.accent_text,
                    border_color=self.app.colors.accent,
                )
            else:
                btn.configure(
                    fg_color=self.app.colors.chip_bg,
                    text_color=self.app.colors.text_secondary,
                    border_color=self.app.colors.border,
                )

    def _handle_add_custom(self) -> None:
        label = simpledialog.askstring(
            "Nouvelle cible",
            "Nom du client cible personnalisé :",
            parent=self.app,
        )
        if not label:
            return
        label = label.strip()
        if not label:
            return
        description = simpledialog.askstring(
            "Description",
            "Décris brièvement cette cible (optionnel) :",
            parent=self.app,
        )
        product_key = self.app.session.product_key
        key = "custom_" + "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
        existing = {e.key for e in self.app.user_state.custom_clients}
        original = key
        i = 2
        while key in existing:
            key = f"{original}_{i}"
            i += 1
        self.app.user_state.custom_clients.append(
            CustomEntry(
                key=key,
                label=label,
                description=(description or "").strip(),
                parent_product_key=product_key,
            )
        )
        self.app.persist()
        self._build_cards()

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._build_cards()
        self._build_contexts()
        for card in self._cards:
            card.set_selected(card.value == self.app.session.client_key)

    def is_valid(self) -> bool:
        return bool(self.app.session.client_key)
