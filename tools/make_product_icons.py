"""Génère les 3 PNG manquants pour Eliks / Publication / Bundles.

Style aligné branding Triskell (indigo/violet/orange/gold) :
- Fond carré arrondi avec dégradé linéaire
- Glyphe blanc centré, lignes propres

Usage : python tools/make_product_icons.py
Sortie : triskell_sales_tunnel/assets/products/{eliks_studio,saas_publication,bundles_mixtes}.png
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "triskell_sales_tunnel" / "assets" / "products"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 192  # source haute déf, sera réduit à l'affichage par CTkImage

# Palette Triskell
INDIGO = (99, 102, 241)
VIOLET = (167, 139, 250)
ORANGE = (249, 115, 22)
GOLD = (212, 179, 90)
WHITE = (255, 255, 255)


def make_gradient_bg(size: int, c1: tuple[int, int, int], c2: tuple[int, int, int], radius_ratio: float = 0.22) -> Image.Image:
    """Carré arrondi avec dégradé linéaire vertical."""
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    for y in range(size):
        t = y / max(1, size - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        bd.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Masque carré arrondi
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    radius = int(size * radius_ratio)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out


# ---------------------------------------------------------------------------
# ELIKS STUDIO — flèche montante (growth), gradient indigo→violet
# ---------------------------------------------------------------------------

def make_eliks(size: int = SIZE) -> Image.Image:
    """Mini chart bar avec flèche montante — symbolise la croissance perf."""
    img = make_gradient_bg(size, INDIGO, VIOLET)
    d = ImageDraw.Draw(img)
    s = size

    # 3 barres verticales croissantes (chart de croissance)
    bar_w = s * 0.11
    base_y = s * 0.74
    bars = [
        (s * 0.28, base_y - s * 0.20),  # plus petite
        (s * 0.46, base_y - s * 0.32),  # moyenne
        (s * 0.64, base_y - s * 0.44),  # plus grande
    ]
    for bx, by in bars:
        d.rounded_rectangle(
            [bx - bar_w / 2, by, bx + bar_w / 2, base_y],
            radius=int(bar_w * 0.25),
            fill=(255, 255, 255, 230),
        )

    # Ligne baseline du graphique (subtile)
    d.line(
        [(s * 0.20, base_y + s * 0.02), (s * 0.80, base_y + s * 0.02)],
        fill=(255, 255, 255, 90),
        width=int(s * 0.012),
    )

    # Flèche en diagonale qui pointe haut-droite (au-dessus des barres)
    p1 = (s * 0.22, s * 0.50)
    p2 = (s * 0.70, s * 0.22)
    line_w = int(s * 0.045)
    d.line([p1, p2], fill=WHITE, width=line_w)

    # Pointe de flèche (triangle plein bien clair, orienté haut-droite)
    arrow_size = s * 0.10
    pt = p2
    d.polygon([
        (pt[0] - arrow_size, pt[1]),                    # gauche
        (pt[0], pt[1]),                                 # extrémité (point haut-droite)
        (pt[0], pt[1] + arrow_size),                    # bas
    ], fill=WHITE)

    return img


# ---------------------------------------------------------------------------
# SAAS PUBLICATION — antenne diffusion, gradient violet→orange
# ---------------------------------------------------------------------------

def make_publication(size: int = SIZE) -> Image.Image:
    img = make_gradient_bg(size, VIOLET, ORANGE)
    d = ImageDraw.Draw(img)

    cx, cy = size / 2, size * 0.62
    s = size
    line_w = int(s * 0.045)

    # Pied vertical (antenne)
    d.line([(cx, cy + s * 0.18), (cx, cy - s * 0.04)], fill=WHITE, width=line_w)

    # Point central
    dot_r = s * 0.05
    d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=WHITE)

    # 3 arcs d'ondes émis vers le haut (de plus en plus grands)
    for i, factor in enumerate((0.16, 0.26, 0.36)):
        r = s * factor
        bbox = [cx - r, cy - r, cx + r, cy + r]
        # Demi-arc supérieur (180°)
        d.arc(bbox, start=200, end=340, fill=WHITE, width=line_w - i)

    # Petits points sur les ondes (signal envoyé)
    pulse_r = s * 0.022
    for fx, fy in ((cx - s * 0.18, cy - s * 0.18), (cx + s * 0.18, cy - s * 0.18)):
        d.ellipse([fx - pulse_r, fy - pulse_r, fx + pulse_r, fy + pulse_r], fill=WHITE)

    return img


# ---------------------------------------------------------------------------
# BUNDLES MIXTES — 3 rectangles superposés (Pro + Perso + Outil)
# ---------------------------------------------------------------------------

def make_bundles(size: int = SIZE) -> Image.Image:
    img = make_gradient_bg(size, INDIGO, ORANGE)
    d = ImageDraw.Draw(img)

    s = size
    # 3 rectangles arrondis empilés en cascade légère
    # rectangle = (x0, y0, x1, y1)
    rect_w = s * 0.46
    rect_h = s * 0.30
    radius = int(s * 0.05)

    # Rect du fond (le plus haut, plus transparent)
    cx = s * 0.50
    base_y = s * 0.65
    offsets = [
        (-s * 0.14, -s * 0.16, (255, 255, 255, 110)),  # arrière-plan, transparent
        ( 0.0,      -s * 0.05, (255, 255, 255, 180)),  # milieu
        ( s * 0.10,  s * 0.05, (255, 255, 255, 255)),  # premier plan, plein
    ]
    for ox, oy, fill in offsets:
        x0 = cx - rect_w / 2 + ox
        y0 = base_y - rect_h / 2 + oy
        x1 = x0 + rect_w
        y1 = y0 + rect_h
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
        # Petit point coloré (badge) sur chaque rect au centre haut
        bdg_r = s * 0.018
        bx = (x0 + x1) / 2
        by = y0 + s * 0.025
        d.ellipse([bx - bdg_r, by - bdg_r, bx + bdg_r, by + bdg_r], fill=GOLD)

    # Petit "+" en haut indique la mixité
    plus_x, plus_y = s * 0.50, s * 0.18
    plus_size = s * 0.05
    d.line([(plus_x - plus_size, plus_y), (plus_x + plus_size, plus_y)], fill=WHITE, width=int(s * 0.025))
    d.line([(plus_x, plus_y - plus_size), (plus_x, plus_y + plus_size)], fill=WHITE, width=int(s * 0.025))

    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    targets = [
        ("eliks_studio.png",      make_eliks),
        ("saas_publication.png",  make_publication),
        ("bundles_mixtes.png",    make_bundles),
    ]
    for filename, factory in targets:
        img = factory()
        out_path = OUT / filename
        img.save(out_path, "PNG")
        print(f"OK {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
