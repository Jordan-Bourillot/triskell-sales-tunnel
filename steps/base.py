"""Classe de base d'un écran du wizard."""

from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk

from .. import theme

if TYPE_CHECKING:
    from ..main import TriskellApp


class WizardStep(ctk.CTkFrame):
    """Frame de base : reçoit l'app + les couleurs, expose enter/leave."""

    title: str = ""
    subtitle: str = ""

    def __init__(self, parent: ctk.CTkFrame, app: "TriskellApp") -> None:
        super().__init__(parent, fg_color=app.colors.bg)
        self.app = app

    def on_enter(self) -> None:
        """Hook appelé quand l'écran devient visible."""

    def on_leave(self) -> None:
        """Hook appelé avant le passage à l'écran suivant."""

    def is_valid(self) -> bool:
        """Indique si l'utilisateur peut passer à l'étape suivante."""
        return True

    def update_colors(self) -> None:
        """Hook appelé sur changement de thème."""
