"""Dialog de paramètres : configuration IA (provider, modèle, clé API)."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

import customtkinter as ctk

from .. import theme
from ..ai import (
    DEFAULT_MODELS,
    PROVIDERS,
    PROVIDER_ANTHROPIC,
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    _decode_key,
    clear_api_key,
    store_api_key,
)
from .components import make_ghost_button, make_primary_button

if TYPE_CHECKING:
    from ..main import TriskellApp


PROVIDER_LABELS = {
    PROVIDER_ANTHROPIC: "Anthropic Claude",
    PROVIDER_OPENAI: "OpenAI GPT",
    PROVIDER_GEMINI: "Google Gemini",
}


class SettingsDialog(ctk.CTkToplevel):
    """Fenêtre modale de paramètres."""

    def __init__(self, app: "TriskellApp") -> None:
        super().__init__(app)
        self.app = app
        self._key_visible = False

        self.title("Paramètres — Triskell Sales Tunnel")
        self.geometry("600x560")
        self.minsize(600, 560)
        self.resizable(False, False)
        self.configure(fg_color=app.colors.bg)
        self.transient(app)
        self.grab_set()

        self._build()
        # Centrer par rapport au parent
        self.update_idletasks()
        x = app.winfo_x() + (app.winfo_width() // 2) - (self.winfo_width() // 2)
        y = app.winfo_y() + (app.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        colors = self.app.colors
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=theme.SPACE_LG, pady=theme.SPACE_LG)

        ctk.CTkLabel(
            outer,
            text="Reformulation IA",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TITLE, "bold"),
            text_color=colors.text_primary,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            outer,
            text=(
                "Configure ton fournisseur IA pour reformuler les templates en 1 clic.\n"
                "Aucune donnée n'est envoyée hors du provider que tu choisis. "
                "Les variables d'env ANTHROPIC_API_KEY / OPENAI_API_KEY ont la priorité."
            ),
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            text_color=colors.text_secondary,
            justify="left",
            wraplength=480,
            anchor="w",
        ).pack(anchor="w", pady=(theme.SPACE_XS, theme.SPACE_LG))

        # Provider
        self._provider_var = tk.StringVar(value=self.app.user_state.ai_provider or PROVIDER_ANTHROPIC)
        self._build_label(outer, "Fournisseur")
        provider_frame = ctk.CTkFrame(outer, fg_color="transparent")
        provider_frame.pack(fill="x", pady=(0, theme.SPACE_MD))
        for i in range(len(PROVIDERS)):
            provider_frame.grid_columnconfigure(i, weight=1, uniform="prov")
        for idx, prov in enumerate(PROVIDERS):
            ctk.CTkRadioButton(
                provider_frame,
                text=PROVIDER_LABELS[prov],
                variable=self._provider_var,
                value=prov,
                command=self._on_provider_change,
                fg_color=colors.accent,
                hover_color=colors.accent_hover,
                text_color=colors.text_primary,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            ).grid(row=0, column=idx, sticky="w", padx=(0, theme.SPACE_MD))

        # Modèle
        self._build_label(outer, "Modèle")
        self._model_var = tk.StringVar(
            value=self.app.user_state.ai_model
            or DEFAULT_MODELS[self._provider_var.get()]
        )
        self._model_entry = ctk.CTkEntry(
            outer,
            textvariable=self._model_var,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            fg_color=colors.bg_alt,
            border_color=colors.border,
            text_color=colors.text_primary,
            corner_radius=theme.RADIUS_SM,
            height=36,
        )
        self._model_entry.pack(fill="x", pady=(0, theme.SPACE_SM))
        ctk.CTkLabel(
            outer,
            text=f"Défaut : {DEFAULT_MODELS[self._provider_var.get()]}",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
            text_color=colors.text_muted,
            anchor="w",
        ).pack(anchor="w", pady=(0, theme.SPACE_MD))

        # Clé API
        self._build_label(outer, "Clé API")
        key_row = ctk.CTkFrame(outer, fg_color="transparent")
        key_row.pack(fill="x", pady=(0, theme.SPACE_SM))
        key_row.grid_columnconfigure(0, weight=1)

        existing_obf = self.app.user_state.ai_api_key_obf
        existing_clear = _decode_key(existing_obf) if existing_obf else ""
        self._key_var = tk.StringVar(value=existing_clear)

        self._key_entry = ctk.CTkEntry(
            key_row,
            textvariable=self._key_var,
            font=(theme.FONT_FAMILY_MONO, theme.FONT_SIZE_BODY),
            fg_color=colors.bg_alt,
            border_color=colors.border,
            text_color=colors.text_primary,
            corner_radius=theme.RADIUS_SM,
            height=36,
            show="•",
        )
        self._key_entry.grid(row=0, column=0, sticky="ew", padx=(0, theme.SPACE_XS))

        self._toggle_btn = make_ghost_button(
            key_row,
            text="👁",
            command=self._toggle_key_visibility,
            colors=colors,
            width=42,
        )
        self._toggle_btn.grid(row=0, column=1)

        ctk.CTkLabel(
            outer,
            text=(
                "⚠ La clé est stockée localement, obfusquée mais NON chiffrée fortement. "
                "Pour une vraie sécurité, utilise une variable d'env."
            ),
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
            text_color=colors.text_muted,
            wraplength=480,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(0, theme.SPACE_LG))

        # Actions
        actions = ctk.CTkFrame(outer, fg_color="transparent")
        actions.pack(fill="x", pady=(theme.SPACE_SM, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=0)
        actions.grid_columnconfigure(2, weight=0)

        make_ghost_button(
            actions,
            text="Effacer la clé",
            command=self._clear,
            colors=colors,
            width=140,
        ).grid(row=0, column=0, sticky="w")

        make_ghost_button(
            actions,
            text="Annuler",
            command=self.destroy,
            colors=colors,
            width=110,
        ).grid(row=0, column=1, padx=(theme.SPACE_SM, theme.SPACE_SM))

        make_primary_button(
            actions,
            text="Enregistrer",
            command=self._save,
            colors=colors,
            width=140,
        ).grid(row=0, column=2)

        self._status = ctk.CTkLabel(
            outer,
            text="",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
            text_color=colors.success,
            anchor="w",
        )
        self._status.pack(anchor="w", pady=(theme.SPACE_SM, 0))

    def _build_label(self, parent: tk.Widget, text: str) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
            text_color=self.app.colors.text_secondary,
            anchor="w",
        ).pack(anchor="w", pady=(0, theme.SPACE_XS))

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_provider_change(self) -> None:
        # Auto-set modèle par défaut si l'utilisateur n'a rien changé
        new_default = DEFAULT_MODELS[self._provider_var.get()]
        if not self._model_var.get().strip() or self._model_var.get() in DEFAULT_MODELS.values():
            self._model_var.set(new_default)

    def _toggle_key_visibility(self) -> None:
        self._key_visible = not self._key_visible
        self._key_entry.configure(show="" if self._key_visible else "•")
        self._toggle_btn.configure(text="🙈" if self._key_visible else "👁")

    def _save(self) -> None:
        provider = self._provider_var.get()
        model = self._model_var.get().strip() or DEFAULT_MODELS[provider]
        key = self._key_var.get().strip()

        self.app.user_state.ai_provider = provider
        self.app.user_state.ai_model = model
        if key:
            store_api_key(self.app.user_state, key)
        else:
            clear_api_key(self.app.user_state)
        self.app.persist()

        self._status.configure(
            text="Paramètres enregistrés ✔",
            text_color=self.app.colors.success,
        )
        self.after(900, self.destroy)

    def _clear(self) -> None:
        self._key_var.set("")
        clear_api_key(self.app.user_state)
        self.app.persist()
        self._status.configure(
            text="Clé effacée.",
            text_color=self.app.colors.text_muted,
        )
