"""Module d'intégration IA — reformulation des templates via Claude ou OpenAI.

DECISION: Appels HTTP via urllib.stdlib (zéro dépendance supplémentaire).
DECISION: Stockage de la clé API dans user_state.json mais OBFUSQUÉE par XOR
+ base64. Ce N'EST PAS du chiffrement fort — c'est une protection minimale
contre la lecture accidentelle (logs, screen-share). Pour une vraie sécurité,
utiliser une variable d'environnement (ANTHROPIC_API_KEY / OPENAI_API_KEY)
qui prime sur la valeur stockée.
DECISION: Modèles par défaut récents (claude-haiku-4-5 / gpt-4o-mini) ;
modifiables via settings.

Sécurité côté utilisateur :
- Variables d'env prioritaires : ANTHROPIC_API_KEY, OPENAI_API_KEY.
- L'app ne logue jamais la clé.
- Stockage local uniquement, jamais transmis ailleurs que vers le provider choisi.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import error as urlerror
from urllib import request as urlrequest

LOG = logging.getLogger("triskell.ai")

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENAI = "openai"
PROVIDER_GEMINI = "gemini"
PROVIDERS = (PROVIDER_ANTHROPIC, PROVIDER_OPENAI, PROVIDER_GEMINI)

DEFAULT_MODELS: Dict[str, str] = {
    PROVIDER_ANTHROPIC: "claude-haiku-4-5",
    PROVIDER_OPENAI: "gpt-4o-mini",
    PROVIDER_GEMINI: "gemini-2.0-flash",
}

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
)

REQUEST_TIMEOUT_SEC = 30
MAX_OUTPUT_TOKENS = 1200

# Clé d'obfuscation (NON un secret — uniquement protection lecture passive).
_OBFUSCATION_KEY = b"triskell-studio-bzh-2026"


# ---------------------------------------------------------------------------
# Erreurs
# ---------------------------------------------------------------------------

class AIError(Exception):
    """Erreur unifiée pour la couche IA (réseau, auth, config, parsing)."""


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@dataclass
class AISettings:
    """Snapshot des paramètres IA résolus (env > state)."""

    provider: str
    api_key: str
    model: str

    @classmethod
    def from_state(cls, user_state: Any) -> "AISettings":
        provider = getattr(user_state, "ai_provider", PROVIDER_ANTHROPIC) or PROVIDER_ANTHROPIC
        if provider not in PROVIDERS:
            provider = PROVIDER_ANTHROPIC

        env_key = {
            PROVIDER_ANTHROPIC: "ANTHROPIC_API_KEY",
            PROVIDER_OPENAI: "OPENAI_API_KEY",
            PROVIDER_GEMINI: "GEMINI_API_KEY",
        }[provider]

        env_value = os.environ.get(env_key, "").strip()
        if env_value:
            api_key = env_value
        else:
            stored = getattr(user_state, "ai_api_key_obf", "") or ""
            api_key = _decode_key(stored) if stored else ""

        model = (
            getattr(user_state, "ai_model", "")
            or DEFAULT_MODELS[provider]
        )
        return cls(provider=provider, api_key=api_key, model=model)


def has_ai_configured(user_state: Any) -> bool:
    """Vrai si un provider IA est configuré et utilisable."""
    s = AISettings.from_state(user_state)
    return bool(s.api_key)


# ---------------------------------------------------------------------------
# Obfuscation simple (PAS de chiffrement fort)
# ---------------------------------------------------------------------------

def _xor_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        return data
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _encode_key(plaintext: str) -> str:
    """Obfusque une clé pour stockage. Réversible localement."""
    if not plaintext:
        return ""
    raw = plaintext.encode("utf-8")
    masked = _xor_bytes(raw, _OBFUSCATION_KEY)
    return base64.b64encode(masked).decode("ascii")


def _decode_key(stored: str) -> str:
    """Inverse de _encode_key. Retourne "" si invalide."""
    if not stored:
        return ""
    try:
        masked = base64.b64decode(stored.encode("ascii"))
    except Exception:  # noqa: BLE001
        return ""
    try:
        return _xor_bytes(masked, _OBFUSCATION_KEY).decode("utf-8")
    except UnicodeDecodeError:
        return ""


def store_api_key(user_state: Any, plaintext: str) -> None:
    """Sauve la clé obfusquée dans le state."""
    user_state.ai_api_key_obf = _encode_key(plaintext) if plaintext else ""


def clear_api_key(user_state: Any) -> None:
    user_state.ai_api_key_obf = ""


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "Tu es un copywriter B2B francophone, ton naturel et chaleureux, style Triskell Studio "
    "(agence digitale bretonne). Reformule le message fourni en gardant : "
    "(1) le même objectif, (2) les mêmes informations factuelles, (3) la même longueur "
    "(±20%). Améliore : naturel, fluidité, accroche, clarté du CTA. "
    "Conserve les placeholders entre crochets `[Comme Ceci]` STRICTEMENT à l'identique "
    "(ne traduis pas, ne reformule pas, ne supprime pas). "
    "Réponds UNIQUEMENT avec le message reformulé, sans préambule ni commentaires."
)


def _build_user_prompt(
    *, original: str, channel: str, client: str, product: str, subject: str
) -> str:
    parts = [
        f"Canal : {channel}",
        f"Cible : {client}",
        f"Produit / offre : {product}",
    ]
    if subject:
        parts.append(f"Objet (à NE PAS reformuler ici, juste contexte) : {subject}")
    parts.append("")
    parts.append("Message à reformuler :")
    parts.append("---")
    parts.append(original)
    parts.append("---")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Appel API
# ---------------------------------------------------------------------------

def generate_rewrite(
    *,
    settings: AISettings,
    original: str,
    channel: str,
    client: str,
    product: str,
    subject: str = "",
) -> str:
    """Reformule `original` via le provider configuré. Lève AIError sur échec."""

    if not settings.api_key:
        raise AIError("Aucune clé API configurée.")

    user_prompt = _build_user_prompt(
        original=original, channel=channel, client=client, product=product, subject=subject
    )

    if settings.provider == PROVIDER_ANTHROPIC:
        return _call_anthropic(settings, user_prompt)
    if settings.provider == PROVIDER_OPENAI:
        return _call_openai(settings, user_prompt)
    if settings.provider == PROVIDER_GEMINI:
        return _call_gemini(settings, user_prompt)
    raise AIError(f"Provider inconnu : {settings.provider}")


def _post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(url, data=body, headers=headers, method="POST")
    try:
        with urlrequest.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as resp:
            raw = resp.read().decode("utf-8")
    except urlerror.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8")[:500]
        except Exception:  # noqa: BLE001
            pass
        if exc.code in (401, 403):
            raise AIError("Clé API refusée (401/403). Vérifie ta clé.") from exc
        if exc.code == 429:
            raise AIError("Quota / rate limit atteint (429). Réessaie plus tard.") from exc
        raise AIError(f"HTTP {exc.code} : {detail or exc.reason}") from exc
    except urlerror.URLError as exc:
        raise AIError(f"Erreur réseau : {exc.reason}") from exc
    except TimeoutError as exc:
        raise AIError("Timeout (>30s). Réessaie.") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIError(f"Réponse non-JSON : {raw[:200]}") from exc


def _call_anthropic(settings: AISettings, user_prompt: str) -> str:
    headers = {
        "content-type": "application/json",
        "x-api-key": settings.api_key,
        "anthropic-version": ANTHROPIC_API_VERSION,
    }
    payload: Dict[str, Any] = {
        "model": settings.model,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": 0.7,
    }
    LOG.info("Appel Anthropic (%s)", settings.model)
    data = _post_json(ANTHROPIC_API_URL, payload, headers)

    content = data.get("content")
    if not isinstance(content, list) or not content:
        raise AIError("Réponse Anthropic inattendue (content vide).")
    first = content[0]
    text = first.get("text") if isinstance(first, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise AIError("Réponse Anthropic inattendue (texte vide).")
    return text.strip()


def _call_gemini(settings: AISettings, user_prompt: str) -> str:
    """Appel Google Gemini (API key en query string, pas en header)."""
    url = GEMINI_API_URL_TEMPLATE.format(
        model=settings.model,
        key=settings.api_key,
    )
    headers = {"content-type": "application/json"}
    payload: Dict[str, Any] = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
        },
    }
    LOG.info("Appel Gemini (%s)", settings.model)
    data = _post_json(url, payload, headers)

    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        # Vérifier les blocages éventuels (safety, prompt_feedback)
        feedback = data.get("promptFeedback") or {}
        block = feedback.get("blockReason")
        if block:
            raise AIError(f"Gemini a bloqué la requête (raison : {block}).")
        raise AIError("Réponse Gemini inattendue (candidates vide).")

    first = candidates[0]
    content = first.get("content") if isinstance(first, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or not parts:
        raise AIError("Réponse Gemini inattendue (parts vide).")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str) or not text.strip():
        raise AIError("Réponse Gemini inattendue (texte vide).")
    return text.strip()


def _call_openai(settings: AISettings, user_prompt: str) -> str:
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {settings.api_key}",
    }
    payload: Dict[str, Any] = {
        "model": settings.model,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    LOG.info("Appel OpenAI (%s)", settings.model)
    data = _post_json(OPENAI_API_URL, payload, headers)

    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AIError("Réponse OpenAI inattendue (choices vide).")
    msg = choices[0].get("message") if isinstance(choices[0], dict) else None
    text = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise AIError("Réponse OpenAI inattendue (texte vide).")
    return text.strip()
