"""Tokens de design — palette Triskell Studio inspirée de l'outil Table Ronde.

Source : `Triskell 0 - Lanceur/style.css` (vars CSS extraites).

Identité Table Ronde :
- Fond gris bleuté chaud (#0f1218 / #161a23 / #1d222e) — moins extrême que le site web
- Indigo doux (#7c7fe9) pour CTAs, plus chaleureux que l'indigo strict
- Trio de marque : Indigo #6366f1 + Violet #a78bfa + Orange #f97316
- Accent or premium : #d4b35a (signature distincte)
- Bordures douces (#262c39), texte chaud (#ecebf5)
- Polices : Quest (display), Inter (body) — fallback Segoe UI
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Trio Triskell (constantes officielles)
# ---------------------------------------------------------------------------

TRISKELL_INDIGO = "#6366F1"
TRISKELL_VIOLET = "#A78BFA"
TRISKELL_ORANGE = "#F97316"

# ---------------------------------------------------------------------------
# Palette Table Ronde — DARK
# ---------------------------------------------------------------------------

D_BG = "#0F1218"
D_BG_2 = "#161A23"
D_BG_3 = "#1D222E"
D_BG_CARD = "#181C27"
D_BG_CARD_HOVER = "#202530"
D_BG_ELEVATED = "#22283A"
D_BORDER = "#262C39"
D_BORDER_STRONG = "#353C4D"

D_HEADER_TOP = "#11141A"
D_HEADER_BOT = "#0F1218"

D_TEXT = "#ECEBF5"
D_TEXT_DIM = "#9DA3B3"
D_TEXT_MUTED = "#6B7180"

D_ACCENT = "#7C7FE9"        # indigo doux principal (CTA)
D_ACCENT_HOT = "#9396F0"    # hover
D_ACCENT_GLOW = "#A78BFA"   # violet light
D_ACCENT_3 = TRISKELL_ORANGE

D_GOLD = "#D4B35A"
D_GOLD_SOFT = "#E6CD87"

# ---------------------------------------------------------------------------
# Palette Table Ronde — LIGHT
# ---------------------------------------------------------------------------

L_BG = "#E9ECF2"
L_BG_2 = "#FFFFFF"
L_BG_3 = "#F3F4F8"
L_BG_CARD = "#FFFFFF"
L_BG_CARD_HOVER = "#F5F6FA"
L_BG_ELEVATED = "#EEF0FF"
L_BORDER = "#D4D7E0"
L_BORDER_STRONG = "#A8ACBA"

L_HEADER_TOP = "#FFFFFF"
L_HEADER_BOT = "#EEF0F5"

L_TEXT = "#14171F"
L_TEXT_DIM = "#4A4F5E"
L_TEXT_MUTED = "#6F7484"

# Sémantique
GREEN = "#4ADE80"
WARNING = "#F59E0B"
DANGER = "#EF4444"


@dataclass(frozen=True)
class ThemeColors:
    """Palette résolue pour un mode (sombre ou clair)."""

    bg: str
    bg_alt: str
    bg_hero: str
    panel: str
    panel_hover: str
    panel_elevated: str
    border: str
    border_strong: str
    border_focus: str

    text_primary: str
    text_secondary: str
    text_muted: str

    accent: str
    accent_hover: str
    accent_glow: str
    accent_text: str
    accent_secondary: str   # violet
    accent_tertiary: str    # orange
    gold: str
    gold_soft: str

    success: str
    danger: str
    warning: str

    chip_bg: str
    chip_active_bg: str
    chip_text: str
    chip_active_text: str

    header_bg: str
    header_top: str
    header_bot: str
    footer_bg: str

    toast_bg: str
    toast_text: str


DARK = ThemeColors(
    bg=D_BG,
    bg_alt=D_BG_2,
    bg_hero=D_BG_3,
    panel=D_BG_CARD,
    panel_hover=D_BG_CARD_HOVER,
    panel_elevated=D_BG_ELEVATED,
    border=D_BORDER,
    border_strong=D_BORDER_STRONG,
    border_focus=D_ACCENT,
    text_primary=D_TEXT,
    text_secondary=D_TEXT_DIM,
    text_muted=D_TEXT_MUTED,
    accent=D_ACCENT,
    accent_hover=D_ACCENT_HOT,
    accent_glow=D_ACCENT_GLOW,
    accent_text="#FFFFFF",
    accent_secondary=TRISKELL_VIOLET,
    accent_tertiary=TRISKELL_ORANGE,
    gold=D_GOLD,
    gold_soft=D_GOLD_SOFT,
    success=GREEN,
    danger=DANGER,
    warning=WARNING,
    chip_bg=D_BG_CARD,
    chip_active_bg=D_ACCENT,
    chip_text=D_TEXT_DIM,
    chip_active_text="#FFFFFF",
    header_bg=D_HEADER_TOP,
    header_top=D_HEADER_TOP,
    header_bot=D_HEADER_BOT,
    footer_bg="#0B0E13",
    toast_bg=D_BG_CARD,
    toast_text=D_TEXT,
)


LIGHT = ThemeColors(
    bg=L_BG,
    bg_alt=L_BG_2,
    bg_hero=L_BG_ELEVATED,
    panel=L_BG_CARD,
    panel_hover=L_BG_CARD_HOVER,
    panel_elevated=L_BG_ELEVATED,
    border=L_BORDER,
    border_strong=L_BORDER_STRONG,
    border_focus=D_ACCENT,
    text_primary=L_TEXT,
    text_secondary=L_TEXT_DIM,
    text_muted=L_TEXT_MUTED,
    accent=D_ACCENT,
    accent_hover=D_ACCENT_HOT,
    accent_glow=TRISKELL_VIOLET,
    accent_text="#FFFFFF",
    accent_secondary=TRISKELL_VIOLET,
    accent_tertiary=TRISKELL_ORANGE,
    gold=D_GOLD,
    gold_soft=D_GOLD_SOFT,
    success=GREEN,
    danger=DANGER,
    warning=WARNING,
    chip_bg=L_BG_3,
    chip_active_bg=D_ACCENT,
    chip_text=L_TEXT_DIM,
    chip_active_text="#FFFFFF",
    header_bg=L_HEADER_TOP,
    header_top=L_HEADER_TOP,
    header_bot=L_HEADER_BOT,
    footer_bg=L_TEXT,
    toast_bg=L_TEXT,
    toast_text="#FFFFFF",
)


# ---------------------------------------------------------------------------
# Typographie
# ---------------------------------------------------------------------------

FONT_FAMILY = "Inter"
FONT_FAMILY_DISPLAY = "Quest"        # police signature Table Ronde, fallback auto si absente
FONT_FAMILY_FALLBACK = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONT_SIZE_HERO = 38
FONT_SIZE_DISPLAY = 26
FONT_SIZE_TITLE = 22
FONT_SIZE_HEADING = 16
FONT_SIZE_BODY = 13
FONT_SIZE_BODY_LG = 14
FONT_SIZE_SMALL = 11
FONT_SIZE_TINY = 10


# ---------------------------------------------------------------------------
# Espacements (4px base)
# ---------------------------------------------------------------------------

SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 18
SPACE_XL = 24
SPACE_2XL = 36
SPACE_3XL = 48

RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 18
RADIUS_XL = 24
RADIUS_PILL = 100

# Tailles fenêtre
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 780
WINDOW_MIN_WIDTH = 960
WINDOW_MIN_HEIGHT = 680


# ---------------------------------------------------------------------------
# Branding texte (chaleureux, accents préservés, ton Table Ronde)
# ---------------------------------------------------------------------------

BRAND_NAME = "Triskell Studio"
BRAND_PRODUCT = "Sales Tunnel"
BRAND_TAGLINE = "Le bon message, au bon moment, pour le bon client."
BRAND_LOCATION = "🌊  Agence bretonne · Fait en Bretagne · 100 % français"
BRAND_WEB = "triskell-studio.fr"
APP_VERSION_LABEL = "v1.1"
