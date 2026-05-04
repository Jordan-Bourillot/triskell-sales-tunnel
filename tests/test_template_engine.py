"""Tests du moteur de templates."""

from __future__ import annotations

import pytest

from triskell_sales_tunnel import template_engine as te


def test_extract_placeholders_simple() -> None:
    text = "Bonjour {prenom}, je suis {mon_prenom} de Triskell."
    assert te.extract_placeholders(text) == ["prenom", "mon_prenom"]


def test_extract_placeholders_dedup() -> None:
    text = "{prenom} {prenom} {nom_entreprise} {prenom}"
    assert te.extract_placeholders(text) == ["prenom", "nom_entreprise"]


def test_extract_placeholders_ignores_non_snake_case() -> None:
    # `{Prenom}` (capitale) et `{}` ne matchent pas.
    text = "{Prenom} {prenom} {} {123x} {ok_2}"
    assert te.extract_placeholders(text) == ["prenom", "ok_2"]


def test_humanize_overrides() -> None:
    assert te.humanize("nom_entreprise") == "Nom entreprise"
    assert te.humanize("mon_prenom") == "Mon prénom"
    assert te.humanize("code_promo") == "Code promo"


def test_humanize_default() -> None:
    assert te.humanize("priorite") == "Priorite"
    assert te.humanize("reseau_social") == "Reseau social"


def test_render_human_replaces_with_brackets() -> None:
    text = "Bonjour {prenom}, ravi de découvrir {nom_entreprise}."
    expected = "Bonjour [Prénom], ravi de découvrir [Nom entreprise]."
    assert te.render_human(text) == expected


def test_render_filled_with_values() -> None:
    text = "Bonjour {prenom} de {nom_entreprise}."
    out = te.render_filled(text, {"prenom": "Jordan", "nom_entreprise": "Triskell"})
    assert out == "Bonjour Jordan de Triskell."


def test_render_filled_keeps_human_for_missing() -> None:
    text = "Bonjour {prenom} de {nom_entreprise}."
    out = te.render_filled(text, {"prenom": "Jordan"})
    assert out == "Bonjour Jordan de [Nom entreprise]."


def test_render_filled_empty_value_falls_back() -> None:
    text = "{prenom} {nom_entreprise}"
    out = te.render_filled(text, {"prenom": "", "nom_entreprise": "Triskell"})
    assert out == "[Prénom] Triskell"


def test_render_dispatch() -> None:
    text = "{prenom}"
    assert te.render(text) == "[Prénom]"
    assert te.render(text, {"prenom": "Jordan"}) == "Jordan"


def test_merge_values_right_wins() -> None:
    a = {"prenom": "A", "nom_entreprise": "Acme"}
    b = {"prenom": "B"}
    assert te.merge_values(a, b) == {"prenom": "B", "nom_entreprise": "Acme"}


def test_collect_all_placeholders_dedup_across_templates() -> None:
    t1 = "{prenom} {nom_entreprise}"
    t2 = "{prenom} {lien_site}"
    assert te.collect_all_placeholders([t1, t2]) == ["prenom", "nom_entreprise", "lien_site"]


def test_has_unfilled() -> None:
    text = "{prenom} {nom_entreprise}"
    assert te.has_unfilled(text, {"prenom": "Jordan"}) is True
    assert te.has_unfilled(text, {"prenom": "Jordan", "nom_entreprise": "Acme"}) is False
    assert te.has_unfilled(text, {"prenom": "  ", "nom_entreprise": "Acme"}) is True


def test_no_placeholder_passthrough() -> None:
    text = "Texte simple sans accolades."
    assert te.render_human(text) == text
    assert te.render_filled(text, {"prenom": "Jordan"}) == text


@pytest.mark.parametrize("ph", ["prenom", "nom_entreprise", "code_promo", "lien_site"])
def test_humanize_no_braces(ph: str) -> None:
    out = te.humanize(ph)
    assert "{" not in out and "}" not in out
