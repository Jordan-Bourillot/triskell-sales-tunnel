"""Tests du catalogue : intégrité, lookups, couverture des canaux."""

from __future__ import annotations

import pytest

from triskell_sales_tunnel import catalog
from triskell_sales_tunnel.catalog import (
    CHANNEL_LABELS,
    PRODUCTS,
    get_client,
    get_product,
    get_template,
    list_channels_for,
)
from triskell_sales_tunnel import template_engine as te


def test_products_have_unique_keys() -> None:
    keys = [p.key for p in PRODUCTS]
    assert len(keys) == len(set(keys)), "Clés produits dupliquées"


def test_clients_have_unique_keys_within_product() -> None:
    for product in PRODUCTS:
        keys = [c.key for c in product.clients]
        assert len(keys) == len(set(keys)), f"Clés clients dupliquées dans {product.key}"


def test_every_client_has_at_least_one_template() -> None:
    for product in PRODUCTS:
        for client in product.clients:
            assert len(client.templates) >= 1, f"Aucun template pour {product.key}/{client.key}"


def test_template_channels_are_known() -> None:
    for product in PRODUCTS:
        for client in product.clients:
            for tpl in client.templates:
                assert tpl.channel in CHANNEL_LABELS, (
                    f"Canal inconnu {tpl.channel} dans {product.key}/{client.key}"
                )


def test_template_bodies_are_non_empty() -> None:
    for product in PRODUCTS:
        for client in product.clients:
            for tpl in client.templates:
                assert tpl.body.strip(), (
                    f"Corps vide pour {product.key}/{client.key}/{tpl.channel}"
                )


def test_email_templates_have_subject() -> None:
    for product in PRODUCTS:
        for client in product.clients:
            for tpl in client.templates:
                if tpl.channel == "email":
                    assert tpl.subject.strip(), (
                        f"Email sans objet : {product.key}/{client.key}"
                    )


def test_lookup_helpers_consistency() -> None:
    for product in PRODUCTS:
        assert get_product(product.key) is product
        for client in product.clients:
            assert get_client(product.key, client.key) is client
            for tpl in client.templates:
                assert get_template(product.key, client.key, tpl.channel) is tpl


def test_list_channels_for() -> None:
    for product in PRODUCTS:
        for client in product.clients:
            channels = list_channels_for(product.key, client.key)
            assert channels == [t.channel for t in client.templates]


def test_lookup_unknown_returns_none() -> None:
    assert get_product("inexistant") is None
    assert get_client("inexistant", "x") is None
    assert get_template("inexistant", "x", "email") is None


@pytest.mark.parametrize("product", PRODUCTS)
def test_priorities_in_valid_range(product: catalog.Product) -> None:
    for client in product.clients:
        assert 1 <= client.priority <= 5, (
            f"Priorité invalide {client.priority} sur {product.key}/{client.key}"
        )


def test_all_template_placeholders_render_humanly() -> None:
    """Aucun placeholder du catalogue ne doit générer de label vide."""
    for product in PRODUCTS:
        for client in product.clients:
            for tpl in client.templates:
                for ph in te.extract_placeholders(tpl.body + " " + tpl.subject):
                    rendered = te.humanize(ph)
                    assert rendered.strip(), (
                        f"Humanize vide pour '{ph}' "
                        f"({product.key}/{client.key}/{tpl.channel})"
                    )
