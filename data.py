"""Persistance utilisateur (state JSON dans %APPDATA%).

DECISION: stockage local uniquement, sans dépendance externe (json stdlib).
DECISION: fichier ouvert atomiquement (write tmp + replace) pour éviter corruption.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

LOG = logging.getLogger("triskell.data")

APP_FOLDER_NAME = "TriskellSalesTunnel"
STATE_FILENAME = "user_state.json"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass
class CustomEntry:
    """Produit ou client cible ajouté manuellement par l'utilisateur."""

    key: str
    label: str
    description: str = ""
    parent_product_key: str = ""  # vide pour un produit, sinon clé du produit parent


@dataclass
class HistoryEntry:
    """Trace d'un template généré."""

    timestamp: str
    product: str
    client: str
    channel: str


@dataclass
class UserState:
    """État global persistant côté utilisateur."""

    custom_products: List[CustomEntry] = field(default_factory=list)
    custom_clients: List[CustomEntry] = field(default_factory=list)
    last_values: Dict[str, str] = field(default_factory=dict)
    history: List[HistoryEntry] = field(default_factory=list)
    appearance_mode: str = "dark"  # "dark" | "light"

    # IA — paramétrage facultatif
    ai_provider: str = "anthropic"   # "anthropic" | "openai"
    ai_model: str = ""               # vide = défaut du provider
    ai_api_key_obf: str = ""         # clé obfusquée (cf. ai.py)

    def remember(self, values: Dict[str, str]) -> None:
        """Mémorise des valeurs non-vides comme défauts pour la prochaine session."""
        for k, v in values.items():
            if v and v.strip():
                self.last_values[k] = v.strip()

    def push_history(self, product: str, client: str, channel: str) -> None:
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            product=product,
            client=client,
            channel=channel,
        )
        self.history.append(entry)
        # Bornage à 50 entrées
        if len(self.history) > 50:
            self.history = self.history[-50:]


# ---------------------------------------------------------------------------
# Localisation du fichier d'état
# ---------------------------------------------------------------------------

def get_data_dir() -> Path:
    """Retourne le dossier de données utilisateur, créé si nécessaire."""
    override = os.environ.get("TRISKELL_DATA_DIR")
    if override:
        path = Path(override)
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        path = base / APP_FOLDER_NAME
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg) if xdg else Path.home() / ".config"
        path = base / APP_FOLDER_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_state_path() -> Path:
    return get_data_dir() / STATE_FILENAME


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def load_state() -> UserState:
    """Charge l'état utilisateur, retourne un état vierge en cas d'erreur."""
    path = get_state_path()
    if not path.exists():
        return UserState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOG.warning("État utilisateur corrompu (%s) — repartir de zéro", exc)
        return UserState()
    return _from_dict(raw)


def save_state(state: UserState) -> None:
    """Sauvegarde atomique."""
    path = get_state_path()
    tmp = path.with_suffix(".tmp")
    payload = json.dumps(_to_dict(state), ensure_ascii=False, indent=2)
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        LOG.error("Sauvegarde état impossible : %s", exc)


# ---------------------------------------------------------------------------
# Sérialisation
# ---------------------------------------------------------------------------

def _to_dict(state: UserState) -> Dict[str, Any]:
    return {
        "custom_products": [asdict(e) for e in state.custom_products],
        "custom_clients": [asdict(e) for e in state.custom_clients],
        "last_values": dict(state.last_values),
        "history": [asdict(h) for h in state.history],
        "appearance_mode": state.appearance_mode,
        "ai_provider": state.ai_provider,
        "ai_model": state.ai_model,
        "ai_api_key_obf": state.ai_api_key_obf,
    }


def _from_dict(raw: Dict[str, Any]) -> UserState:
    return UserState(
        custom_products=[CustomEntry(**e) for e in raw.get("custom_products", [])],
        custom_clients=[CustomEntry(**e) for e in raw.get("custom_clients", [])],
        last_values=dict(raw.get("last_values", {})),
        history=[HistoryEntry(**h) for h in raw.get("history", [])],
        appearance_mode=raw.get("appearance_mode", "dark"),
        ai_provider=raw.get("ai_provider", "anthropic"),
        ai_model=raw.get("ai_model", ""),
        ai_api_key_obf=raw.get("ai_api_key_obf", ""),
    )
