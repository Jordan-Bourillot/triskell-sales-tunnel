"""Moteur de templates.

Responsabilités :
- Détecter les placeholders `{snake_case}` dans un texte.
- Convertir un placeholder vers/depuis sa forme lisible `[Format Lisible]`.
- Rendre un template :
    * version "humaine"   : placeholders affichés `[Prénom]` (lisible mais non rempli).
    * version "remplie"   : placeholders remplacés par les valeurs fournies (ou `[Prénom]` si absent).
- Lister les placeholders nécessaires dans l'ordre d'apparition.

DECISION: regex stricte `\\{([a-z][a-z0-9_]*)\\}` (snake_case). Tout texte hors pattern reste intact.
DECISION: placeholders inconnus restent affichés `[Format Lisible]` plutôt que de planter.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List

PLACEHOLDER_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")


# Surcharges manuelles pour des cas où le snake_case → Title Case naïf donne moche
# ou pour préserver les accents français.
_HUMAN_OVERRIDES: Dict[str, str] = {
    "prenom": "Prénom",
    "mon_prenom": "Mon prénom",
    "lien_site": "Lien site",
    "nom_entreprise": "Nom entreprise",
    "region_secteur": "Région / Secteur",
    "article_post_recent": "Article ou post récent",
    "sujet_expertise": "Sujet d'expertise",
    "produit_phare": "Produit phare",
    "friction_1": "Friction 1",
    "friction_2": "Friction 2",
    "friction_3": "Friction 3",
    "projet_site": "Projet / Site",
    "produit_programme": "Produit ou programme",
    "prix_moyen": "Prix moyen",
    "sujet_recent": "Sujet récent",
    "specialite": "Spécialité",
    "code_promo": "Code promo",
    "date_promo": "Date fin promo",
    "telephone": "Téléphone",
    "metier": "Métier",
    "trimestre": "Trimestre",
    "segment": "Segment / Niche",
    "agence": "Nom de l'agence",
}


def humanize(placeholder: str) -> str:
    """Convertit `nom_entreprise` -> `Nom entreprise` (capitalisation 1er mot, reste en lower)."""
    if placeholder in _HUMAN_OVERRIDES:
        return _HUMAN_OVERRIDES[placeholder]
    parts = placeholder.split("_")
    if not parts:
        return placeholder
    head = parts[0].capitalize()
    if len(parts) == 1:
        return head
    return head + " " + " ".join(parts[1:])


def extract_placeholders(template: str) -> List[str]:
    """Liste des placeholders dans l'ordre d'apparition (sans doublon)."""
    seen: List[str] = []
    for match in PLACEHOLDER_RE.finditer(template):
        ph = match.group(1)
        if ph not in seen:
            seen.append(ph)
    return seen


def render_human(template: str) -> str:
    """Remplace `{prenom}` par `[Prénom]` pour lecture sans valeurs."""
    return PLACEHOLDER_RE.sub(lambda m: f"[{humanize(m.group(1))}]", template)


def render_filled(template: str, values: Dict[str, str]) -> str:
    """Remplace les placeholders par leurs valeurs.

    Si une valeur est absente ou vide, on garde la forme `[Format Lisible]`.
    """
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        val = values.get(key, "").strip() if values else ""
        if val:
            return val
        return f"[{humanize(key)}]"

    return PLACEHOLDER_RE.sub(replace, template)


def render(template: str, values: Dict[str, str] | None = None) -> str:
    """Rendu unifié : si `values` fourni, version remplie, sinon version humaine."""
    if values is None:
        return render_human(template)
    return render_filled(template, values)


def merge_values(*sources: Dict[str, str] | None) -> Dict[str, str]:
    """Fusionne plusieurs sources de valeurs ; les sources de droite l'emportent."""
    out: Dict[str, str] = {}
    for s in sources:
        if not s:
            continue
        for k, v in s.items():
            if v is not None:
                out[k] = v
    return out


def collect_all_placeholders(templates: Iterable[str]) -> List[str]:
    """Union ordonnée de tous les placeholders trouvés dans une liste de templates."""
    seen: List[str] = []
    for t in templates:
        for ph in extract_placeholders(t):
            if ph not in seen:
                seen.append(ph)
    return seen


def has_unfilled(template: str, values: Dict[str, str]) -> bool:
    """Vrai si au moins un placeholder n'est pas rempli avec une valeur non vide."""
    for ph in extract_placeholders(template):
        if not values.get(ph, "").strip():
            return True
    return False
