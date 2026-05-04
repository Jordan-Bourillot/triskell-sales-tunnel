"""Génère l'icône Windows de l'app : .ico multi-tailles + .png pour fallback.

Reproduit fidèlement le logo officiel Triskell (3 feuilles spiralées
indigo/violet/orange, fond gris bleuté Table Ronde).

Source du path : og-image.svg du site officiel
   M18,18 C20,15 22,10 20,6 C18,2 13,3 13,7.5 C13,12 16,15.5 18,18Z
   + rotations 120° / 240°.

Sortie :
   triskell_sales_tunnel/assets/triskell_icon.ico   (16, 24, 32, 48, 64, 128, 256)
   triskell_sales_tunnel/assets/triskell_icon.png   (256x256, fallback POSIX)

Usage : python tools/make_app_icon.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "triskell_sales_tunnel" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

# Couleurs officielles
LEAF_INDIGO = (99, 102, 241, 255)
LEAF_VIOLET = (167, 139, 250, 255)
LEAF_ORANGE = (249, 115, 22, 255)
GLOW_VIOLET = (167, 139, 250, 80)
GLOW_GOLD   = (212, 179, 90, 60)
BG_DARK     = (15, 18, 24, 255)   # palette Table Ronde
CENTER_DOT  = (15, 18, 24, 255)

# Source SVG : viewBox 0 0 36 36, centre = (18, 18)
SVG_VIEWBOX = 36
SVG_CENTER = 18

# Path SVG du leaf : 3 segments Bézier cubique
LEAF_PATH = [
    # (start, ctrl1, ctrl2, end)
    ((18, 18), (20, 15), (22, 10), (20, 6)),
    ((20, 6),  (18, 2),  (13, 3),  (13, 7.5)),
    ((13, 7.5),(13, 12), (16, 15.5),(18, 18)),
]


def cubic_bezier(p0, p1, p2, p3, steps: int = 24):
    """Échantillonne `steps`+1 points le long d'une Bézier cubique."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def leaf_points():
    """Liste de points (en coordonnées SVG) pour une feuille."""
    pts = []
    for (p0, p1, p2, p3) in LEAF_PATH:
        seg = cubic_bezier(p0, p1, p2, p3, steps=24)
        if pts:
            seg = seg[1:]  # éviter doublon au début
        pts.extend(seg)
    return pts


def transform_points(points, scale: float, cx: float, cy: float, angle_deg: float):
    """Translate au centre du SVG (18,18), scale, rotate, retransfert au centre canvas."""
    rad = math.radians(angle_deg)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    out = []
    for (x, y) in points:
        ox = (x - SVG_CENTER) * scale
        oy = (y - SVG_CENTER) * scale
        rx = ox * cos_t - oy * sin_t
        ry = ox * sin_t + oy * cos_t
        out.append((cx + rx, cy + ry))
    return out


def draw_halo(draw: ImageDraw.ImageDraw, size: int, cx: float, cy: float):
    """Halos concentriques violet + or pour effet glow (rendu doux via alpha)."""
    # Halo or (extérieur)
    for r_pct, alpha in ((0.48, 30), (0.42, 50)):
        r = size * r_pct
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(212, 179, 90, alpha),
            width=max(1, size // 64),
        )
    # Halo violet (intérieur)
    for r_pct, alpha in ((0.36, 70), (0.30, 90)):
        r = size * r_pct
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(167, 139, 250, alpha),
            width=max(1, size // 60),
        )


def make_logo(size: int = 256) -> Image.Image:
    """Compose le logo Triskell complet à la taille `size`."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    cx = cy = size / 2

    # 1. Fond carré arrondi sombre (style icône desktop)
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    radius = int(size * 0.22)
    bd.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG_DARK)
    img.alpha_composite(bg)

    # 2. Halos doux derrière les feuilles
    halo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo, "RGBA")
    draw_halo(halo_draw, size, cx, cy)
    img.alpha_composite(halo)

    # 3. 3 feuilles indigo / violet / orange à 0° / 120° / 240°
    leaf_scale = (size / SVG_VIEWBOX) * 0.78  # occupe 78% du logo

    base_pts = leaf_points()
    leaf_colors = (LEAF_INDIGO, LEAF_VIOLET, LEAF_ORANGE)
    for i, color in enumerate(leaf_colors):
        angle = i * 120
        pts = transform_points(base_pts, leaf_scale, cx, cy, angle)
        # ImageDraw.polygon n'a pas de smoothing natif mais nos points Bézier
        # sont densifiés (3 × 25 = 75 points), donc le tracé est fluide.
        draw.polygon(pts, fill=color)

    # 4. Disque central
    center_r = size * 0.075
    draw.ellipse(
        [cx - center_r, cy - center_r, cx + center_r, cy + center_r],
        fill=CENTER_DOT,
    )

    return img


def main() -> None:
    # Génération multi-tailles pour le .ico Windows
    sizes = (16, 24, 32, 48, 64, 128, 256)
    images = [make_logo(s) for s in sizes]
    biggest = images[-1]

    # Sauvegarde .ico (Windows lit la taille adaptée selon le contexte)
    ico_path = OUT / "triskell_icon.ico"
    biggest.save(ico_path, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"OK {ico_path}  ({ico_path.stat().st_size // 1024} KB, {len(sizes)} tailles)")

    # PNG 256x256 fallback (Linux taskbar, README, etc.)
    png_path = OUT / "triskell_icon.png"
    biggest.save(png_path, format="PNG")
    print(f"OK {png_path}  ({png_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
