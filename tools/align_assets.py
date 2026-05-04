"""Aligne l'icône .ico Windows sur le PNG officiel Table Ronde + génère l'OG image landing.

- Source : Triskell 0 - Lanceur/assets/apps/triskell-sales-tunnel.png (512×512 officiel)
- Sortie 1 : triskell_sales_tunnel/assets/triskell_icon.ico (multi-tailles 16-256)
- Sortie 1bis : triskell_sales_tunnel/assets/triskell_icon.png (256×256 fallback POSIX)
- Sortie 2 : landing/public/og-image.png (1200×630, hero card branded)

Usage : python tools/align_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PARENT = ROOT.parent  # Triskell Studio root
SRC_PNG = PARENT / "Triskell 0 - Lanceur" / "assets" / "apps" / "triskell-sales-tunnel.png"

ASSETS = ROOT / "triskell_sales_tunnel" / "assets"
LANDING_PUB = ROOT / "landing" / "public"

# Couleurs landing (alignées Table Ronde)
BG_DARK = (15, 18, 24, 255)
GOLD = (212, 179, 90, 255)
INDIGO = (99, 102, 241, 255)
VIOLET = (167, 139, 250, 255)
ORANGE = (249, 115, 22, 255)
TEXT = (236, 235, 245, 255)
TEXT_DIM = (157, 163, 179, 255)


# ---------------------------------------------------------------------------
# 1) ICONE Windows multi-tailles depuis le PNG Table Ronde
# ---------------------------------------------------------------------------

def make_icon():
    if not SRC_PNG.exists():
        raise FileNotFoundError(f"Source PNG introuvable : {SRC_PNG}")
    src = Image.open(SRC_PNG).convert("RGBA")

    # Tailles standards Windows
    sizes = (16, 24, 32, 48, 64, 128, 256)
    base = src.resize((256, 256), Image.LANCZOS)

    ico_path = ASSETS / "triskell_icon.ico"
    base.save(ico_path, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"OK {ico_path}  ({ico_path.stat().st_size // 1024} KB, {len(sizes)} tailles)")

    png_path = ASSETS / "triskell_icon.png"
    base.save(png_path, format="PNG")
    print(f"OK {png_path}  ({png_path.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
# 2) OG IMAGE 1200x630 pour la landing
# ---------------------------------------------------------------------------

def _make_radial_orb(size, color_rgb, alpha=80):
    """Crée un disque flouté simulé via gradient circulaire."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = cy = size / 2
    for r in range(size // 2, 0, -2):
        # alpha décroissant vers l'extérieur
        ratio = r / (size / 2)
        a = int(alpha * (1 - ratio) ** 2)
        d = ImageDraw.Draw(img)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color_rgb + (a,))
    return img


def _try_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Tente de charger Inter/Segoe UI, fallback default."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",   # Segoe UI Bold
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:  # noqa: BLE001
            continue
    return ImageFont.load_default()


def make_og_image():
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), BG_DARK)

    # Orbs flous indigo + violet + orange en arrière-plan
    orb_indigo = _make_radial_orb(700, INDIGO[:3], alpha=140)
    orb_violet = _make_radial_orb(900, VIOLET[:3], alpha=80)
    orb_orange = _make_radial_orb(500, ORANGE[:3], alpha=80)
    img.alpha_composite(orb_indigo, (-200, -250))
    img.alpha_composite(orb_violet, (700, 100))
    img.alpha_composite(orb_orange, (450, 380))

    # Grille subtile (lignes blanches transparentes)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 60):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
    for y in range(0, H, 60):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)
    img.alpha_composite(grid)

    # Logo Triskell à gauche
    if SRC_PNG.exists():
        logo = Image.open(SRC_PNG).convert("RGBA").resize((180, 180), Image.LANCZOS)
        img.alpha_composite(logo, (90, 105))

    d = ImageDraw.Draw(img)

    # "TRISKELL STUDIO" en gold
    font_brand = _try_font(28)
    d.text((298, 130), "TRISKELL  STUDIO", fill=GOLD, font=font_brand)

    # Titre principal
    font_title = _try_font(78)
    d.text((298, 165), "Sales Tunnel", fill=TEXT, font=font_title)

    # Tagline
    font_tag = _try_font(36)
    d.text((90, 360), "Le bon message,", fill=TEXT, font=font_tag)
    d.text((90, 408), "au bon moment,", fill=VIOLET, font=font_tag)
    d.text((90, 456), "pour le bon client.", fill=TEXT, font=font_tag)

    # Footer URL + chips
    font_small = _try_font(20)
    d.text((90, 555), "prospect.triskell-studio.fr", fill=GOLD, font=font_small)

    # Chips à droite : 4 stats
    chip_x = 720
    chip_y = 555
    font_chip = _try_font(18)
    chips = ["Gratuit", "100 % local", "Windows 10/11"]
    pad_h = 12
    cx = chip_x
    for c in chips:
        bbox = d.textbbox((0, 0), c, font=font_chip)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.rounded_rectangle(
            [cx, chip_y - 6, cx + w + pad_h * 2, chip_y + h + 8],
            radius=20,
            fill=(255, 255, 255, 18),
            outline=(255, 255, 255, 40),
            width=1,
        )
        d.text((cx + pad_h, chip_y), c, fill=TEXT_DIM, font=font_chip)
        cx += w + pad_h * 2 + 8

    # Sauvegarde
    out = LANDING_PUB / "og-image.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"OK {out}  ({out.stat().st_size // 1024} KB, 1200x630)")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    LANDING_PUB.mkdir(parents=True, exist_ok=True)
    make_icon()
    make_og_image()


if __name__ == "__main__":
    main()
