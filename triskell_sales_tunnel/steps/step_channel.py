"""Étape 3 — Choix du canal d'acquisition."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import customtkinter as ctk

from .. import theme
from ..catalog import (
    CHANNEL_ICONS,
    CHANNEL_LABELS,
    get_client,
    list_channels_for,
)
from ..widgets.components import ChannelChip
from .base import WizardStep

if TYPE_CHECKING:
    from ..main import TriskellApp


class StepChannel(WizardStep):
    """Affiche les canaux disponibles ; les non-disponibles sont signalés."""

    title = "Sur quel canal on l'envoie ?"
    subtitle = "Les canaux marqués ★ ont un template optimisé pour ce duo produit + cible."

    def __init__(self, parent: ctk.CTkFrame, app: "TriskellApp") -> None:
        super().__init__(parent, app)
        self._chips: List[ChannelChip] = []

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

        # Section "recommandés"
        self._reco_label = ctk.CTkLabel(
            self,
            text="★  Canaux optimisés pour cette cible",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_HEADING, "bold"),
            text_color=app.colors.accent,
            anchor="w",
        )
        self._reco_label.pack(anchor="w", padx=theme.SPACE_2XL, pady=(theme.SPACE_MD, theme.SPACE_SM))

        self._reco_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._reco_frame.pack(fill="x", padx=theme.SPACE_2XL)

        # Section "tous les canaux"
        ctk.CTkLabel(
            self,
            text="Autres canaux  ·  template générique chaleureux",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_HEADING, "bold"),
            text_color=app.colors.text_secondary,
            anchor="w",
        ).pack(anchor="w", padx=theme.SPACE_2XL, pady=(theme.SPACE_LG, theme.SPACE_SM))

        self._other_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._other_frame.pack(fill="x", padx=theme.SPACE_2XL, pady=(0, theme.SPACE_LG))

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        for w in self._reco_frame.winfo_children():
            w.destroy()
        for w in self._other_frame.winfo_children():
            w.destroy()
        self._chips = []

        recommended = list_channels_for(
            self.app.session.product_key, self.app.session.client_key
        )

        # Disposition en grille fluide — chips recommandés
        for idx, channel_key in enumerate(recommended):
            chip = ChannelChip(
                self._reco_frame,
                label=CHANNEL_LABELS.get(channel_key, channel_key),
                icon=CHANNEL_ICONS.get(channel_key, "•"),
                value=channel_key,
                colors=self.app.colors,
                on_click=self._handle_select,
                recommended=True,
            )
            chip.grid(row=idx // 5, column=idx % 5, padx=(0, theme.SPACE_MD), pady=(0, theme.SPACE_MD))
            self._chips.append(chip)

        # Tous les autres
        others = [k for k in CHANNEL_LABELS.keys() if k not in recommended]
        for idx, channel_key in enumerate(others):
            chip = ChannelChip(
                self._other_frame,
                label=CHANNEL_LABELS[channel_key],
                icon=CHANNEL_ICONS.get(channel_key, "•"),
                value=channel_key,
                colors=self.app.colors,
                on_click=self._handle_select,
                recommended=False,
            )
            chip.grid(row=idx // 5, column=idx % 5, padx=(0, theme.SPACE_MD), pady=(0, theme.SPACE_MD))
            self._chips.append(chip)

    def _handle_select(self, value: str) -> None:
        self.app.session.channel = value
        for chip in self._chips:
            chip.set_selected(chip.value == value)
        self.app.update_nav_state()

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._build()
        for chip in self._chips:
            chip.set_selected(chip.value == self.app.session.channel)

    def is_valid(self) -> bool:
        return bool(self.app.session.channel)
