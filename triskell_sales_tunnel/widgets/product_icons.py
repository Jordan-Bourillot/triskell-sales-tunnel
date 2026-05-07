"""Mapping des icônes par produit + chargement CTkImage / emoji fallback.

Les PNG officiels sont copiés depuis Triskell 0 - Lanceur/assets/apps.
Pour les produits sans PNG dispo (Eliks SVG, Publication, Bundles), on
utilise un emoji uniformément stylé.

DECISION: chemin relatif au module pour fonctionner aussi bien depuis
les sources que depuis le binaire PyInstaller (qui copie le dossier
triskell_sales_tunnel/assets dans _internal/).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image  # type: ignore[import-untyped]
import customtkinter as ctk

LOG = logging.getLogger("triskell.product_icons")

# Mapping product_key -> (icon_filename | None, emoji fallback)
# Tous les PNG sont les officiels Triskell Studio (copiés depuis Triskell 0 - Lanceur).
ICON_MAP: dict[str, Tuple[Optional[str], str]] = {
    # Pros
    "triskell_studio":      ("triskell_studio.png",      "🌐"),
    "eliks_studio":         ("eliks_studio.png",         "🚀"),
    "le_denicheur":         ("le_denicheur.png",         "🔭"),
    "alphacast":            ("alphacast.png",            "📡"),
    "alphabeast":           ("alphabeast.png",           "🤖"),
    "outils_batiment":      ("outils_batiment.png",      "🔧"),
    "pack_electricien_pro": ("pack_electricien_pro.png", "⚡"),
    # Particuliers
    "suite_des_heros":      ("suite_des_heros.png",      "🛠"),
    "delinote":             ("delinote.png",             "📝"),
    "studio_pdf":           ("studio_pdf.png",           "📄"),
    "bobeez":               ("bobeez.png",               "📸"),
    # Mixte
    "bundles_mixtes":       ("bundles_mixtes.png",       "📦"),
}

EMOJI_DEFAULT = "✦"


def _assets_dir() -> Path:
    """Retourne le chemin du dossier assets/products (sources OU exe PyInstaller)."""
    # En mode binaire PyInstaller : sys._MEIPASS pointe vers le dossier _internal
    if hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS"))
        candidate = base / "triskell_sales_tunnel" / "assets" / "products"
        if candidate.exists():
            return candidate
    # Mode sources : chemin relatif au module
    return Path(__file__).resolve().parent.parent / "assets" / "products"


def get_icon_emoji(product_key: str) -> str:
    """Retourne l'emoji fallback pour un produit (toujours valide)."""
    return ICON_MAP.get(product_key, (None, EMOJI_DEFAULT))[1]


def get_icon_image(product_key: str, size: int = 44) -> Optional[ctk.CTkImage]:
    """Charge l'icône PNG en CTkImage si disponible, sinon None.

    Retourne None si le produit n'a pas de PNG ou si le fichier est introuvable
    (l'appelant doit alors fallback sur un emoji).
    """
    entry = ICON_MAP.get(product_key)
    if not entry or not entry[0]:
        return None
    filename = entry[0]
    path = _assets_dir() / filename
    if not path.exists():
        LOG.debug("Icon introuvable : %s", path)
        return None
    try:
        img = Image.open(path).convert("RGBA")
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    except Exception as exc:  # noqa: BLE001
        LOG.warning("Chargement icône %s échoué : %s", filename, exc)
        return None
