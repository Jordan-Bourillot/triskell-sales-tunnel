"""Application Triskell Sales Tunnel — entrypoint.

Architecture :
- TriskellApp (CTk) : fenêtre racine, gère le thème, la session, la navigation wizard.
- WizardSession      : état de la session (produit / client / canal / valeurs).
- 4 WizardStep        : empilées sur le même conteneur, affichées une à la fois.

DECISION: navigation par index, sans router dynamique. Les 4 étapes sont fixes.
DECISION: thème commuté à la volée en recréant les widgets (méthode la plus fiable
avec CustomTkinter qui ne supporte pas re-color complet à chaud).
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import List

import customtkinter as ctk

from . import __app_name__, __version__, theme
from .data import UserState, load_state, save_state
from .steps.base import WizardStep
from .steps.step_channel import StepChannel
from .steps.step_client import StepClient
from .steps.step_product import StepProduct
from .steps.step_template import StepTemplate
from .updater import APP_VERSION as UPDATER_VERSION, UpdateStatus, updater
from .widgets.components import (
    Toast,
    make_ghost_button,
    make_primary_button,
    make_subtle_button,
)
from .widgets.settings_dialog import SettingsDialog
from .widgets.step_indicator import StepIndicator
from .widgets.triskell_logo import TriskellLogo

LOG = logging.getLogger("triskell.main")

STEP_LABELS: List[str] = ["Produit", "Cible", "Canal", "Message"]


@dataclass
class WizardSession:
    """État de la session en cours (réinitialisable)."""

    product_key: str = ""
    client_key: str = ""
    context_key: str = ""
    channel: str = ""

    def reset(self) -> None:
        self.product_key = ""
        self.client_key = ""
        self.context_key = ""
        self.channel = ""


class TriskellApp(ctk.CTk):
    """Fenêtre principale."""

    def __init__(self) -> None:
        super().__init__()
        self.user_state: UserState = load_state()
        self.session = WizardSession()
        self._current_step_index = 0
        self._steps: List[WizardStep] = []

        ctk.set_appearance_mode("dark" if self.user_state.appearance_mode == "dark" else "light")
        self.colors: theme.ThemeColors = theme.DARK if self.user_state.appearance_mode == "dark" else theme.LIGHT

        self._configure_window()
        self._build_layout()
        self._show_step(0)

        # Auto-update : check passif au démarrage (1.5s après boot pour ne pas bloquer)
        updater.add_listener(self._on_update_status)
        self.after(1500, lambda: updater.check_for_updates(async_=True))

    # ------------------------------------------------------------------
    # Configuration fenêtre
    # ------------------------------------------------------------------

    def _configure_window(self) -> None:
        self.title(f"{theme.BRAND_NAME} — {theme.BRAND_PRODUCT}")
        self.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=self.colors.bg)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._set_app_icon()

    def _build_header_logo(self) -> ctk.CTkBaseClass:
        """Construit le logo header. PNG officiel si dispo, sinon TriskellLogo Canvas."""
        import sys
        from pathlib import Path
        from PIL import Image

        if hasattr(sys, "_MEIPASS"):
            base = Path(getattr(sys, "_MEIPASS")) / "triskell_sales_tunnel" / "assets"
        else:
            base = Path(__file__).resolve().parent / "assets"

        png = base / "triskell_icon.png"
        if png.exists():
            try:
                img = Image.open(png).convert("RGBA")
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                label = ctk.CTkLabel(self._header, text="", image=ctk_img, fg_color="transparent")
                # Garder la ref pour eviter le GC
                self._header_logo_image = ctk_img
                label.grid(row=0, column=0, padx=(theme.SPACE_2XL, theme.SPACE_LG), pady=theme.SPACE_LG)
                return label
            except Exception as exc:  # noqa: BLE001
                LOG.warning("Logo PNG illisible (%s), fallback Canvas", exc)

        # Fallback Canvas Bezier
        canvas_logo = TriskellLogo(
            self._header,
            size=60,
            bg=self.colors.header_bg,
            leaf_indigo=self.colors.accent,
            leaf_violet=self.colors.accent_secondary,
            leaf_orange=self.colors.accent_tertiary,
            center=self.colors.bg,
            glow=self.colors.accent_glow,
            gold=self.colors.gold,
        )
        canvas_logo.grid(row=0, column=0, padx=(theme.SPACE_2XL, theme.SPACE_LG), pady=theme.SPACE_LG)
        return canvas_logo

    def _set_app_icon(self) -> None:
        """Définit l'icône fenêtre + taskbar Windows depuis le .ico embarqué."""
        import sys
        from pathlib import Path

        # Résolution du chemin (sources OU exe PyInstaller)
        if hasattr(sys, "_MEIPASS"):
            base = Path(getattr(sys, "_MEIPASS")) / "triskell_sales_tunnel" / "assets"
        else:
            base = Path(__file__).resolve().parent / "assets"

        ico_path = base / "triskell_icon.ico"
        png_path = base / "triskell_icon.png"

        try:
            if ico_path.exists() and sys.platform == "win32":
                self.iconbitmap(default=str(ico_path))
            elif png_path.exists():
                # Fallback Linux/Mac : iconphoto avec un PhotoImage
                import tkinter as tk
                photo = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, photo)
                # Garder la ref pour éviter le GC
                self._app_icon_photo = photo
        except Exception as exc:  # noqa: BLE001
            LOG.warning("Impossible de charger l'icône de l'app : %s", exc)

    def _build_layout(self) -> None:
        self._build_header()
        self._build_indicator()
        self._build_steps_container()
        self._build_footer()
        self._build_app_footer()

    def _build_header(self) -> None:
        self._header = ctk.CTkFrame(
            self,
            fg_color=self.colors.header_bg,
            corner_radius=0,
            height=88,
        )
        self._header.grid(row=0, column=0, sticky="ew")
        self._header.grid_propagate(False)
        self._header.grid_columnconfigure(1, weight=1)

        # Logo : on utilise le PNG officiel Triskell (cohérent avec .ico Windows + Table Ronde)
        # Fallback Canvas Bezier si le PNG est introuvable (dev local sans assets).
        # _build_header_logo() s'occupe du .grid() interne.
        self._logo = self._build_header_logo()

        # Brand block (style Table Ronde : nom en display, sous-label en gold uppercase)
        brand_frame = ctk.CTkFrame(self._header, fg_color="transparent")
        brand_frame.grid(row=0, column=1, sticky="w", pady=theme.SPACE_MD)

        # Ligne 1 : "Triskell Sales Tunnel" en grand + version pill
        line1 = ctk.CTkFrame(brand_frame, fg_color="transparent")
        line1.pack(anchor="w")
        ctk.CTkLabel(
            line1,
            text="Triskell",
            font=(theme.FONT_FAMILY_DISPLAY, theme.FONT_SIZE_DISPLAY, "bold"),
            text_color=self.colors.text_primary,
        ).pack(side="left")
        ctk.CTkLabel(
            line1,
            text=" Sales Tunnel",
            font=(theme.FONT_FAMILY_DISPLAY, theme.FONT_SIZE_DISPLAY, "bold"),
            text_color=self.colors.accent,
        ).pack(side="left")
        # Version badge
        ctk.CTkLabel(
            line1,
            text=theme.APP_VERSION_LABEL,
            font=(theme.FONT_FAMILY_MONO, theme.FONT_SIZE_TINY),
            text_color=self.colors.text_muted,
            fg_color="transparent",
            corner_radius=theme.RADIUS_PILL,
        ).pack(side="left", padx=(theme.SPACE_SM, 0), pady=(10, 0))

        # Ligne 2 : badge breton "STUDIO" en gold + tagline
        sub_row = ctk.CTkFrame(brand_frame, fg_color="transparent")
        sub_row.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            sub_row,
            text="TRISKELL  STUDIO",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
            text_color=self.colors.gold,
        ).pack(side="left")
        ctk.CTkLabel(
            sub_row,
            text="  ·  ",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
            text_color=self.colors.text_muted,
        ).pack(side="left")
        ctk.CTkLabel(
            sub_row,
            text=theme.BRAND_LOCATION,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TINY),
            text_color=self.colors.text_secondary,
        ).pack(side="left")

        # Right actions
        right_actions = ctk.CTkFrame(self._header, fg_color="transparent")
        right_actions.grid(row=0, column=2, sticky="e", padx=theme.SPACE_2XL)

        self._theme_btn = make_subtle_button(
            right_actions,
            text="☀  Mode clair" if self.user_state.appearance_mode == "dark" else "🌙  Mode sombre",
            command=self._toggle_theme,
            colors=self.colors,
            width=130,
        )
        self._theme_btn.pack(side="right", padx=(theme.SPACE_XS, 0))

        self._settings_btn = make_subtle_button(
            right_actions,
            text="⚙  Paramètres",
            command=self._open_settings,
            colors=self.colors,
            width=130,
        )
        self._settings_btn.pack(side="right", padx=(theme.SPACE_XS, 0))

        # Bouton mise à jour — width 0 = auto (CTk s'adapte au texte) pour ne pas tronquer
        # les états longs ("⚡ Installer v1.2.0").
        self._update_btn = make_subtle_button(
            right_actions,
            text="↻  Vérifier MAJ",
            command=self._handle_update_click,
            colors=self.colors,
            width=0,
        )
        self._update_btn.pack(side="right", padx=(theme.SPACE_XS, 0), ipadx=8)

        # Filet de séparation : gradient indigo → violet → orange (signature site officiel)
        accent_bar = ctk.CTkFrame(self, fg_color="transparent", height=3, corner_radius=0)
        accent_bar.grid(row=0, column=0, sticky="sew")
        accent_bar.grid_columnconfigure(0, weight=1)
        accent_bar.grid_columnconfigure(1, weight=1)
        accent_bar.grid_columnconfigure(2, weight=1)
        ctk.CTkFrame(accent_bar, fg_color=self.colors.accent, height=3, corner_radius=0).grid(row=0, column=0, sticky="ew")
        ctk.CTkFrame(accent_bar, fg_color=self.colors.accent_secondary, height=3, corner_radius=0).grid(row=0, column=1, sticky="ew")
        ctk.CTkFrame(accent_bar, fg_color=self.colors.accent_tertiary, height=3, corner_radius=0).grid(row=0, column=2, sticky="ew")

    def _build_indicator(self) -> None:
        # Bandeau de progression sur fond bg_alt pour démarcation visuelle
        wrapper = ctk.CTkFrame(self, fg_color=self.colors.bg_hero, corner_radius=0)
        wrapper.grid(row=1, column=0, sticky="ew")
        self._indicator = StepIndicator(wrapper, STEP_LABELS, self.colors)
        # Patch couleur de fond du canvas pour matcher le wrapper
        self._indicator._canvas.configure(bg=self.colors.bg_hero)
        self._indicator._colors = self.colors
        self._indicator.pack(fill="x", padx=0, pady=0)

    def _build_steps_container(self) -> None:
        self._steps_container = ctk.CTkFrame(self, fg_color=self.colors.bg)
        self._steps_container.grid(row=2, column=0, sticky="nsew")
        self._steps_container.grid_rowconfigure(0, weight=1)
        self._steps_container.grid_columnconfigure(0, weight=1)

        self._steps = [
            StepProduct(self._steps_container, self),
            StepClient(self._steps_container, self),
            StepChannel(self._steps_container, self),
            StepTemplate(self._steps_container, self),
        ]
        for s in self._steps:
            s.grid(row=0, column=0, sticky="nsew")
            s.grid_remove()

    def _build_footer(self) -> None:
        self._footer = ctk.CTkFrame(
            self,
            fg_color=self.colors.bg_alt,
            corner_radius=0,
            height=82,
        )
        self._footer.grid(row=3, column=0, sticky="ew")
        self._footer.grid_propagate(False)
        self._footer.grid_columnconfigure(1, weight=1)

        self._back_btn = make_ghost_button(
            self._footer,
            text="←  Précédent",
            command=self._go_back,
            colors=self.colors,
            width=140,
        )
        self._back_btn.grid(row=0, column=0, padx=(theme.SPACE_2XL, theme.SPACE_SM), pady=theme.SPACE_LG)

        self._reset_btn = make_ghost_button(
            self._footer,
            text="↻  Recommencer",
            command=self._restart,
            colors=self.colors,
            width=140,
        )
        self._reset_btn.grid(row=0, column=1, sticky="w", padx=theme.SPACE_SM, pady=theme.SPACE_LG)

        self._next_btn = make_primary_button(
            self._footer,
            text="Suivant  →",
            command=self._go_next,
            colors=self.colors,
            width=180,
            height=46,
        )
        self._next_btn.grid(row=0, column=2, padx=(theme.SPACE_SM, theme.SPACE_2XL), pady=theme.SPACE_LG)

    def _build_app_footer(self) -> None:
        # Bandeau footer micro signé Triskell
        self._app_footer = ctk.CTkFrame(
            self,
            fg_color=self.colors.footer_bg,
            corner_radius=0,
            height=30,
        )
        self._app_footer.grid(row=4, column=0, sticky="ew")
        self._app_footer.grid_propagate(False)
        self._app_footer.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self._app_footer,
            text=theme.BRAND_TAGLINE,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TINY, "italic"),
            text_color=self.colors.text_muted,
        ).grid(row=0, column=0, sticky="w", padx=theme.SPACE_LG)

        ctk.CTkLabel(
            self._app_footer,
            text=f"{theme.BRAND_NAME}  ·  {theme.BRAND_WEB}",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TINY, "bold"),
            text_color=self.colors.text_secondary,
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            self._app_footer,
            text=f"{theme.BRAND_PRODUCT}  ·  {theme.APP_VERSION_LABEL}",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TINY),
            text_color=self.colors.text_muted,
        ).grid(row=0, column=2, sticky="e", padx=theme.SPACE_LG)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _show_step(self, index: int) -> None:
        if not 0 <= index < len(self._steps):
            return
        if 0 <= self._current_step_index < len(self._steps):
            self._steps[self._current_step_index].on_leave()
            self._steps[self._current_step_index].grid_remove()
        self._current_step_index = index
        step = self._steps[index]
        step.grid()
        step.on_enter()
        self._indicator.set_step(index)
        self.update_nav_state()

    def _go_next(self) -> None:
        step = self._steps[self._current_step_index]
        if not step.is_valid():
            return
        if self._current_step_index < len(self._steps) - 1:
            self._show_step(self._current_step_index + 1)

    def _go_back(self) -> None:
        if self._current_step_index > 0:
            self._show_step(self._current_step_index - 1)

    def _restart(self) -> None:
        self.session.reset()
        self._show_step(0)

    def update_nav_state(self) -> None:
        idx = self._current_step_index
        self._back_btn.configure(state="disabled" if idx == 0 else "normal")

        if idx == len(self._steps) - 1:
            self._next_btn.configure(text="✓  Terminer", command=self._finish)
        else:
            self._next_btn.configure(text="Suivant  →", command=self._go_next)

        is_valid = self._steps[idx].is_valid() if idx < len(self._steps) else True
        self._next_btn.configure(state="normal" if is_valid else "disabled")

    def _finish(self) -> None:
        self.persist()
        self.toast("Session enregistrée. Place à la prochaine !", kind="success")
        self._restart()

    # ------------------------------------------------------------------
    # Persistance & UI helpers
    # ------------------------------------------------------------------

    def persist(self) -> None:
        try:
            save_state(self.user_state)
        except Exception as exc:  # noqa: BLE001
            LOG.error("Erreur persistance : %s", exc)

    def toast(self, message: str, kind: str = "success") -> None:
        Toast(self, message=message, colors=self.colors, kind=kind)

    def _on_close(self) -> None:
        self.persist()
        self.destroy()

    # ------------------------------------------------------------------
    # Thème / paramètres
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        SettingsDialog(self)

    # ------------------------------------------------------------------
    # Auto-update
    # ------------------------------------------------------------------

    def _on_update_status(self, status: UpdateStatus) -> None:
        # Le callback peut être déclenché depuis un thread du updater.
        # On revient sur le thread Tk via .after(0, ...).
        self.after(0, lambda s=status: self._apply_update_status(s))

    def _apply_update_status(self, status: UpdateStatus) -> None:
        try:
            if status.phase == "checking":
                self._update_btn.configure(text="↻  Vérification…")
            elif status.phase == "not-available":
                self._update_btn.configure(text="✓  À jour")
            elif status.phase == "available":
                self._update_btn.configure(
                    text=f"⬇  v{status.next_version} dispo",
                    fg_color=self.colors.gold,
                    text_color="#0F1218",
                    border_color=self.colors.gold,
                )
            elif status.phase == "downloading":
                self._update_btn.configure(text=f"⬇  {status.percent}%")
            elif status.phase == "ready":
                self._update_btn.configure(
                    text=f"⚡  Installer v{status.next_version}",
                    fg_color=self.colors.accent,
                    text_color=self.colors.accent_text,
                    border_color=self.colors.accent,
                )
                self.toast(
                    f"Mise à jour v{status.next_version} prête. Clique pour installer.",
                    kind="info",
                )
            elif status.phase == "error":
                self._update_btn.configure(text="↻  Vérifier MAJ")
        except Exception:  # noqa: BLE001
            pass

    def _handle_update_click(self) -> None:
        phase = updater.status.phase
        if phase == "ready":
            updater.install()
        elif phase in ("idle", "not-available", "error"):
            updater.check_for_updates(async_=True)
        # phases "checking" / "downloading" / "available" : on ne fait rien

    def _toggle_theme(self) -> None:
        new_mode = "light" if self.user_state.appearance_mode == "dark" else "dark"
        self.user_state.appearance_mode = new_mode
        ctk.set_appearance_mode(new_mode)
        self.colors = theme.DARK if new_mode == "dark" else theme.LIGHT
        self.persist()
        for child in list(self.winfo_children()):
            child.destroy()
        self.configure(fg_color=self.colors.bg)
        self.grid_rowconfigure(2, weight=1)
        self._build_layout()
        self._show_step(self._current_step_index)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def run() -> None:
    configure_logging()
    LOG.info("Démarrage %s v%s", __app_name__, __version__)
    ctk.set_default_color_theme("blue")
    app = TriskellApp()
    app.mainloop()


if __name__ == "__main__":
    run()
