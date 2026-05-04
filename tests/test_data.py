"""Tests de la persistance utilisateur."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from triskell_sales_tunnel import data


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirige TRISKELL_DATA_DIR vers un répertoire temporaire pour chaque test."""
    monkeypatch.setenv("TRISKELL_DATA_DIR", str(tmp_path))
    return tmp_path


def test_load_state_returns_default_when_file_absent() -> None:
    state = data.load_state()
    assert state.custom_products == []
    assert state.custom_clients == []
    assert state.last_values == {}
    assert state.history == []
    assert state.appearance_mode == "dark"


def test_save_then_load_roundtrip(isolated_data_dir: Path) -> None:
    state = data.UserState()
    state.custom_products.append(data.CustomEntry(key="custom_x", label="X", description="desc"))
    state.last_values["prenom"] = "Jordan"
    state.push_history("triskell_studio", "tpe_pme", "email")
    data.save_state(state)

    reloaded = data.load_state()
    assert len(reloaded.custom_products) == 1
    assert reloaded.custom_products[0].label == "X"
    assert reloaded.last_values == {"prenom": "Jordan"}
    assert len(reloaded.history) == 1
    assert reloaded.history[0].product == "triskell_studio"


def test_save_creates_atomic_file(isolated_data_dir: Path) -> None:
    state = data.UserState()
    data.save_state(state)
    assert (isolated_data_dir / data.STATE_FILENAME).exists()
    # Pas de .tmp résiduel
    assert not list(isolated_data_dir.glob("*.tmp"))


def test_load_state_with_corrupted_file(isolated_data_dir: Path) -> None:
    (isolated_data_dir / data.STATE_FILENAME).write_text("{not json", encoding="utf-8")
    state = data.load_state()
    assert state.custom_products == []
    assert state.last_values == {}


def test_remember_skips_empty_values() -> None:
    state = data.UserState()
    state.remember({"prenom": "Jordan", "nom_entreprise": "  ", "lien_site": "triskell-studio.fr"})
    assert state.last_values == {"prenom": "Jordan", "lien_site": "triskell-studio.fr"}


def test_history_capped_at_50() -> None:
    state = data.UserState()
    for i in range(60):
        state.push_history("p", "c", f"channel_{i % 5}")
    assert len(state.history) == 50
    # Les 50 derniers conservés (i = 10..59)
    assert state.history[0].channel == "channel_0"  # i=10 => 10%5 = 0


def test_get_data_dir_uses_env_override(isolated_data_dir: Path) -> None:
    assert data.get_data_dir() == isolated_data_dir
