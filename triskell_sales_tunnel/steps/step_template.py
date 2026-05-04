"""Étape 4 — Template final : aperçu, placeholders éditables, copie / export."""

from __future__ import annotations

import logging
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Dict, List

import customtkinter as ctk

from .. import template_engine, theme
from ..ai import AIError, AISettings, generate_rewrite, has_ai_configured
from ..catalog import CHANNEL_LABELS, get_client, get_product, get_template
from ..exporters import ExportPayload, export_docx, export_pdf, export_txt
from ..widgets.components import make_ghost_button, make_primary_button
from .base import WizardStep

LOG = logging.getLogger("triskell.step_template")

if TYPE_CHECKING:
    from ..main import TriskellApp


# Template fallback générique quand aucun template dédié n'existe.
GENERIC_TEMPLATE_BY_CHANNEL: Dict[str, str] = {
    "email": (
        "Bonjour {prenom},\n\n"
        "Je suis {mon_prenom} de Triskell Studio. Je me permets de vous écrire au sujet de "
        "{nom_entreprise} : on a une offre qui pourrait correspondre à votre situation actuelle.\n\n"
        "{accroche_libre}\n\n"
        "Si ça vous parle, on en discute 15 minutes cette semaine ?\n\n"
        "Cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
    ),
    "linkedin": (
        "Bonjour {prenom}, ravi de vous voir dans mon réseau. Chez Triskell Studio on accompagne "
        "{nom_entreprise} sur {besoin_principal}. Si ça vous intéresse, 15 min suffisent pour "
        "regarder ensemble. Belle journée."
    ),
    "instagram_dm": (
        "Hello {prenom} 👋 J'ai jeté un œil à {nom_entreprise} et j'ai des pistes concrètes "
        "à partager sur {besoin_principal}. Si ça vous intéresse, je vous envoie tout ça."
    ),
    "whatsapp": (
        "Bonjour {prenom}, c'est {mon_prenom} de Triskell Studio. On peut aider {nom_entreprise} "
        "sur {besoin_principal}. 15 min cette semaine pour en parler ?"
    ),
    "facebook_messenger": (
        "Bonjour {prenom}, j'ai vu {nom_entreprise} et j'ai 2-3 pistes concrètes pour vous aider sur "
        "{besoin_principal}. Si ça vous intéresse, on en discute. — {mon_prenom}, Triskell Studio."
    ),
    "twitter_dm": (
        "Hello {prenom}, vu votre activité sur {sujet_recent} — top. On a une offre Triskell qui "
        "pourrait coller à {nom_entreprise} sur {besoin_principal}. 15 min ?"
    ),
}


class StepTemplate(WizardStep):
    """Génère, affiche et personnalise le template final."""

    title = "Ton message est déjà prêt."
    subtitle = "Remplis les champs pour personnaliser, puis copie ou exporte. La régénération applique tes valeurs au texte."

    def __init__(self, parent: ctk.CTkFrame, app: "TriskellApp") -> None:
        super().__init__(parent, app)
        self._field_vars: Dict[str, tk.StringVar] = {}
        self._field_widgets: List[ctk.CTkEntry] = []
        self._reveal_visible = False
        self._current_template_text = ""
        self._current_subject = ""

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=theme.SPACE_2XL, pady=(theme.SPACE_LG, theme.SPACE_SM))
        ctk.CTkLabel(
            header,
            text=self.title,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_TITLE, "bold"),
            text_color=app.colors.text_primary,
            anchor="w",
        ).pack(anchor="w")
        self._context_label = ctk.CTkLabel(
            header,
            text=self.subtitle,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            text_color=app.colors.text_secondary,
            anchor="w",
            justify="left",
            wraplength=820,
        )
        self._context_label.pack(anchor="w", pady=(theme.SPACE_XS, 0))

        # Colonne gauche — preview
        left = ctk.CTkFrame(self, fg_color=app.colors.panel, corner_radius=theme.RADIUS_LG, border_width=1, border_color=app.colors.border)
        left.grid(row=1, column=0, sticky="nsew", padx=(theme.SPACE_2XL, theme.SPACE_MD), pady=(0, theme.SPACE_LG))
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self._channel_label = ctk.CTkLabel(
            left,
            text="",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_HEADING, "bold"),
            text_color=app.colors.accent,
            anchor="w",
        )
        self._channel_label.grid(row=0, column=0, sticky="ew", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_XS))

        self._subject_label = ctk.CTkLabel(
            left,
            text="",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY, "bold"),
            text_color=app.colors.text_primary,
            anchor="w",
            wraplength=540,
            justify="left",
        )
        self._subject_label.grid(row=1, column=0, sticky="ew", padx=theme.SPACE_LG, pady=(0, theme.SPACE_SM))

        self._preview = ctk.CTkTextbox(
            left,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
            text_color=app.colors.text_primary,
            fg_color=app.colors.bg_alt,
            border_color=app.colors.border,
            border_width=1,
            wrap="word",
            corner_radius=theme.RADIUS_MD,
        )
        self._preview.grid(row=2, column=0, sticky="nsew", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        # Colonne droite — placeholders + actions
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=(theme.SPACE_MD, theme.SPACE_2XL), pady=(0, theme.SPACE_LG))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._reveal_btn = make_ghost_button(
            right,
            text="🔓 Révéler les champs à remplir",
            command=self._toggle_reveal,
            colors=app.colors,
            width=320,
        )
        self._reveal_btn.grid(row=0, column=0, sticky="ew", pady=(0, theme.SPACE_SM))

        self._fields_scroll = ctk.CTkScrollableFrame(
            right,
            fg_color=app.colors.panel,
            corner_radius=theme.RADIUS_MD,
            label_text="",
            scrollbar_button_color=app.colors.border,
            scrollbar_button_hover_color=app.colors.accent,
        )
        self._fields_scroll.grid(row=1, column=0, sticky="nsew")
        self._fields_scroll.grid_remove()  # caché par défaut

        # Boutons d'action en bas de la colonne droite
        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", pady=(theme.SPACE_MD, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        make_primary_button(
            actions,
            text="📋  Copier",
            command=self._copy_to_clipboard,
            colors=app.colors,
            width=160,
        ).grid(row=0, column=0, sticky="ew", padx=(0, theme.SPACE_XS), pady=theme.SPACE_XS)

        make_ghost_button(
            actions,
            text="🔁  Régénérer",
            command=self._regenerate,
            colors=app.colors,
            width=160,
        ).grid(row=0, column=1, sticky="ew", padx=(theme.SPACE_XS, 0), pady=theme.SPACE_XS)

        make_ghost_button(
            actions,
            text="📄  Export .txt",
            command=lambda: self._export("txt"),
            colors=app.colors,
            width=160,
        ).grid(row=1, column=0, sticky="ew", padx=(0, theme.SPACE_XS), pady=theme.SPACE_XS)

        make_ghost_button(
            actions,
            text="📕  Export .pdf",
            command=lambda: self._export("pdf"),
            colors=app.colors,
            width=160,
        ).grid(row=1, column=1, sticky="ew", padx=(theme.SPACE_XS, 0), pady=theme.SPACE_XS)

        make_ghost_button(
            actions,
            text="📘  Export .docx",
            command=lambda: self._export("docx"),
            colors=app.colors,
            width=160,
        ).grid(row=2, column=0, sticky="ew", padx=(0, theme.SPACE_XS), pady=theme.SPACE_XS)

        self._ai_btn = make_ghost_button(
            actions,
            text="✨  Reformuler IA",
            command=self._rewrite_with_ai,
            colors=app.colors,
            width=160,
        )
        self._ai_btn.grid(row=2, column=1, sticky="ew", padx=(theme.SPACE_XS, 0), pady=theme.SPACE_XS)

        self._status_label = ctk.CTkLabel(
            right,
            text="",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL),
            text_color=app.colors.success,
            anchor="w",
        )
        self._status_label.grid(row=3, column=0, sticky="ew", pady=(theme.SPACE_SM, 0))

    # ------------------------------------------------------------------
    # Construction des champs
    # ------------------------------------------------------------------

    def _resolve_template_text(self) -> str:
        sess = self.app.session
        tpl = get_template(sess.product_key, sess.client_key, sess.channel, sess.context_key)
        if tpl:
            self._current_subject = tpl.subject
            return tpl.body
        # Fallback générique
        self._current_subject = ""
        return GENERIC_TEMPLATE_BY_CHANNEL.get(
            sess.channel,
            (
                "Bonjour {prenom},\n\nMessage de prospection pour {nom_entreprise}.\n\n"
                "{accroche_libre}\n\nCordialement,\n{mon_prenom} — Triskell Studio"
            ),
        )

    def _build_fields(self) -> None:
        for w in self._fields_scroll.winfo_children():
            w.destroy()
        self._field_vars = {}
        self._field_widgets = []

        placeholders = template_engine.collect_all_placeholders(
            [self._current_template_text, self._current_subject]
        )

        if not placeholders:
            ctk.CTkLabel(
                self._fields_scroll,
                text="Aucun champ à remplir — votre template est déjà prêt.",
                text_color=self.app.colors.text_muted,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
                wraplength=320,
                justify="left",
            ).pack(padx=theme.SPACE_MD, pady=theme.SPACE_MD)
            return

        for ph in placeholders:
            label = template_engine.humanize(ph)
            ctk.CTkLabel(
                self._fields_scroll,
                text=label,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_SMALL, "bold"),
                text_color=self.app.colors.text_secondary,
                anchor="w",
            ).pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_SM, 2))

            var = tk.StringVar(value=self.app.user_state.last_values.get(ph, ""))
            entry = ctk.CTkEntry(
                self._fields_scroll,
                textvariable=var,
                placeholder_text=label,
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY),
                fg_color=self.app.colors.bg_alt,
                border_color=self.app.colors.border,
                text_color=self.app.colors.text_primary,
                corner_radius=theme.RADIUS_SM,
                height=34,
            )
            entry.pack(fill="x", padx=theme.SPACE_MD, pady=(0, theme.SPACE_XS))
            var.trace_add("write", lambda *_args, k=ph: self._on_field_changed(k))
            self._field_vars[ph] = var
            self._field_widgets.append(entry)

    # ------------------------------------------------------------------
    # Reveal / regenerate / actions
    # ------------------------------------------------------------------

    def _toggle_reveal(self) -> None:
        self._reveal_visible = not self._reveal_visible
        if self._reveal_visible:
            self._fields_scroll.grid()
            self._reveal_btn.configure(text="🔒 Masquer les champs")
        else:
            self._fields_scroll.grid_remove()
            self._reveal_btn.configure(text="🔓 Révéler les champs à remplir")

    def _current_values(self) -> Dict[str, str]:
        return {k: v.get() for k, v in self._field_vars.items()}

    def _on_field_changed(self, _key: str) -> None:
        self._render_preview()

    def _regenerate(self) -> None:
        # Force le rebuild du template (utile après un changement caché ou pour réinitialiser).
        self._current_template_text = self._resolve_template_text()
        self._build_fields()
        self._render_preview()
        self._status_label.configure(
            text="Template régénéré avec les valeurs actuelles.",
            text_color=self.app.colors.success,
        )
        self.after(2200, lambda: self._status_label.configure(text=""))

    def _render_preview(self) -> None:
        values = self._current_values()
        body = template_engine.render_filled(self._current_template_text, values) if values else template_engine.render_human(self._current_template_text)
        subject = ""
        if self._current_subject:
            subject = template_engine.render_filled(self._current_subject, values) if values else template_engine.render_human(self._current_subject)

        self._preview.configure(state="normal")
        self._preview.delete("1.0", "end")
        self._preview.insert("1.0", body)
        self._preview.configure(state="normal")  # gardée éditable pour ajustement manuel

        if subject:
            self._subject_label.configure(text=f"Objet : {subject}")
            self._subject_label.grid()
        else:
            self._subject_label.configure(text="")
            self._subject_label.grid_remove()

    def _copy_to_clipboard(self) -> None:
        body = self._preview.get("1.0", "end-1c")
        subject = self._subject_label.cget("text")
        full = (subject + "\n\n" + body).strip() if subject else body

        ok = self._copy_text(full)
        if ok:
            self._persist_last_values()
            self._status_label.configure(
                text="Copié dans le presse-papier ✔",
                text_color=self.app.colors.success,
            )
        else:
            self._status_label.configure(
                text="Échec de la copie système.",
                text_color=self.app.colors.danger,
            )
        self.after(2200, lambda: self._status_label.configure(text=""))

    def _copy_text(self, text: str) -> bool:
        try:
            import pyperclip  # type: ignore[import-untyped]
            pyperclip.copy(text)
            return True
        except Exception as exc:  # noqa: BLE001 — fallback explicite
            LOG.info("pyperclip indisponible (%s), fallback Tk", exc)
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            return True
        except tk.TclError as exc:
            LOG.error("Copie Tk impossible : %s", exc)
            return False

    def _build_export_payload(self) -> ExportPayload:
        body = self._preview.get("1.0", "end-1c").rstrip()
        subject_label = self._subject_label.cget("text") or ""
        # Le label affiche `Objet : ...` — on récupère uniquement la valeur.
        subject = subject_label.split("Objet :", 1)[-1].strip() if subject_label else ""

        product = get_product(self.app.session.product_key)
        client = get_client(self.app.session.product_key, self.app.session.client_key)

        return ExportPayload(
            body=body,
            subject=subject,
            product_label=product.label if product else self.app.session.product_key,
            client_label=client.label if client else self.app.session.client_key,
            channel_label=CHANNEL_LABELS.get(self.app.session.channel, self.app.session.channel),
        )

    def _export(self, fmt: str) -> None:
        payload = self._build_export_payload()
        ext = {"txt": ".txt", "pdf": ".pdf", "docx": ".docx"}[fmt]
        types = {
            "txt": [("Texte", "*.txt"), ("Tous fichiers", "*.*")],
            "pdf": [("PDF", "*.pdf"), ("Tous fichiers", "*.*")],
            "docx": [("Word", "*.docx"), ("Tous fichiers", "*.*")],
        }[fmt]
        suggested = (
            f"triskell_{self.app.session.product_key}_{self.app.session.channel}"
            f"_{datetime.now().strftime('%Y%m%d_%H%M')}{ext}"
        )
        path_str = filedialog.asksaveasfilename(
            parent=self.app,
            defaultextension=ext,
            initialfile=suggested,
            filetypes=types,
            title=f"Exporter en {fmt.upper()}",
        )
        if not path_str:
            return
        path = Path(path_str)
        try:
            if fmt == "txt":
                export_txt(payload, path)
            elif fmt == "pdf":
                export_pdf(payload, path)
            elif fmt == "docx":
                export_docx(payload, path)
            self._persist_last_values()
            self._status_label.configure(
                text=f"Exporté → {path.name}",
                text_color=self.app.colors.success,
            )
        except (OSError, ImportError) as exc:
            LOG.error("Export %s impossible : %s", fmt, exc)
            messagebox.showerror(
                "Export",
                f"Impossible d'exporter en {fmt.upper()} : {exc}\n\n"
                f"Vérifie que les dépendances sont installées (pip install -r requirements.txt).",
            )
        self.after(3000, lambda: self._status_label.configure(text=""))

    # ------------------------------------------------------------------
    # Reformulation IA
    # ------------------------------------------------------------------

    def _rewrite_with_ai(self) -> None:
        if not has_ai_configured(self.app.user_state):
            messagebox.showinfo(
                "Reformulation IA",
                "Aucun fournisseur IA configuré.\n\n"
                "Va dans le menu Paramètres (⚙ en haut à droite) pour ajouter ta clé "
                "Anthropic ou OpenAI.",
            )
            return

        payload = self._build_export_payload()
        original_body = payload.body
        if not original_body.strip():
            return

        self._ai_btn.configure(state="disabled", text="✨  IA en cours…")
        self._status_label.configure(
            text="Reformulation en cours, ~5-15s…",
            text_color=self.app.colors.text_muted,
        )
        self.update_idletasks()

        settings = AISettings.from_state(self.app.user_state)

        # DECISION: appel synchrone bloquant (acceptable, max 30s).
        # Pour une vraie UX, à passer en thread + after() — voir BACKLOG.md.
        try:
            new_body = generate_rewrite(
                settings=settings,
                original=original_body,
                channel=payload.channel_label,
                client=payload.client_label,
                product=payload.product_label,
                subject=payload.subject,
            )
        except AIError as exc:
            self._status_label.configure(
                text=f"Erreur IA : {exc}",
                text_color=self.app.colors.danger,
            )
            self._ai_btn.configure(state="normal", text="✨  Reformuler IA")
            return

        # Met à jour la preview
        self._preview.configure(state="normal")
        self._preview.delete("1.0", "end")
        self._preview.insert("1.0", new_body)

        self._status_label.configure(
            text="Texte reformulé. Tu peux ajuster avant copie / export.",
            text_color=self.app.colors.success,
        )
        self._ai_btn.configure(state="normal", text="✨  Reformuler IA")
        self.after(4000, lambda: self._status_label.configure(text=""))

    def _persist_last_values(self) -> None:
        values = self._current_values()
        self.app.user_state.remember(values)
        self.app.user_state.push_history(
            product=self.app.session.product_key,
            client=self.app.session.client_key,
            channel=self.app.session.channel,
        )
        self.app.persist()

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        product = get_product(self.app.session.product_key)
        client = get_client(self.app.session.product_key, self.app.session.client_key)
        product_label = product.label if product else self.app.session.product_key
        client_label = client.label if client else self.app.session.client_key
        channel_label = CHANNEL_LABELS.get(self.app.session.channel, self.app.session.channel)
        self._channel_label.configure(text=f"{channel_label}")
        self._context_label.configure(
            text=f"{product_label}  →  {client_label}  →  {channel_label}",
        )

        self._current_template_text = self._resolve_template_text()
        self._build_fields()
        self._render_preview()
