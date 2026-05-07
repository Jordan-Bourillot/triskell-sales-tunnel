# AlphaPitch v1.1 — Backlog implémentation

> Créé le 2026-05-04 par session Claude précédente.
> Stack : Python 3.10+ / customtkinter 5.2+ / urllib stdlib.
> v1.0 actuelle : templates Triskell hardcodés (catalog.py 1762 lignes), reformulation IA déjà OK.

## 🎯 Objectif

Transformer AlphaPitch d'un outil interne (templates pushent les produits Triskell de Jordan) en **produit vendable** où :
- Le client renseigne **son** activité dans un formulaire onboarding
- L'IA **génère** des templates personnalisés selon son profil (au lieu de prendre les Triskell-templates statiques)
- Mode "Founder" caché pour Jordan : conserve les templates pre-bakés Triskell

## 📐 Architecture

### Nouveaux fichiers

#### `triskell_sales_tunnel/profile.py`
Dataclass `UserProfile` + load/save JSON dans `user_state.json`.

```python
@dataclass
class UserProfile:
    activity: str           # "Agence webdesign pour artisans"
    target: str             # "Artisans BTP, 1-5 employés"
    tone: str               # "chaleureux" | "pro" | "direct" | "fun"
    differentiators: list[str]  # 3 phrases courtes
    first_name: str
    site_url: str

    def is_complete(self) -> bool: ...
```

#### `triskell_sales_tunnel/widgets/onboarding_dialog.py`
Dialog customtkinter en 5 écrans :
1. Activité / produit principal (textarea 200 chars)
2. Cible idéale (textarea 200 chars)
3. Ton (radio 4 options)
4. 3 différenciateurs (3 inputs)
5. Prénom + lien site (2 inputs)

Bouton "Suivant" / "Précédent" / "Terminer". Validation à chaque étape (champs requis non vides).

### Fichiers modifiés

#### `triskell_sales_tunnel/ai.py`
Ajouter à côté de `generate_rewrite()` :

```python
SYSTEM_PROMPT_GENERATE = """
Tu es un expert en prospection écrite francophone (ton naturel, breton chaleureux,
style Triskell Studio). Tu génères un message de prospection pour [CANAL] vers [CIBLE]
afin de vendre [PRODUIT_USER].

Profil expéditeur :
- Activité : {activity}
- Cible générale : {target}
- Ton souhaité : {tone}
- Différenciateurs vs concurrents : {differentiators}
- Prénom : {first_name}
- Lien : {site_url}

Contraintes STRICTES :
- Français correct, accents préservés
- Placeholders révélables EXACTEMENT sous ce format : [Prénom], [Nom entreprise], [Lien site]
- NE COMMENCE PAS par "Bonjour" — sois plus créatif sur l'accroche
- Longueur : 80-150 mots pour DM (LinkedIn, Insta, WhatsApp), 200-300 mots pour Email
- Pas de préambule, pas de signature multiline, pas d'emojis sauf si tone = "fun"
- Tu réponds UNIQUEMENT avec le message, sans guillemets, sans commentaires
"""

def generate_template(
    *,
    settings: AISettings,
    profile: UserProfile,
    product: str,
    client_target: str,
    channel: str,
) -> str:
    """Génère un template depuis zéro, appelé en cache miss."""
```

#### `triskell_sales_tunnel/data.py`
Étendre `UserState` :

```python
@dataclass
class UserState:
    # ... existant
    profile: UserProfile | None = None
    template_cache: dict[str, str] = field(default_factory=dict)
    # clé cache = sha1(product + client + channel + profile.version)

    @property
    def is_admin(self) -> bool:
        # Founder mode : env var TRISKELL_FOUNDER=1 OU
        # email last_login dans la liste admin
        return os.environ.get("TRISKELL_FOUNDER") == "1"
```

#### `triskell_sales_tunnel/main.py`
- Au boot : `if not state.profile and not state.is_admin: open_onboarding()`
- Step 4 (template generation) :
  - Si admin : prendre le template de `catalog.py` (comportement actuel)
  - Sinon : `cache_key = hash(product+client+channel)`, lookup `state.template_cache[cache_key]`, si miss → `ai.generate_template()`, store cache
- Settings dialog : nouvel onglet "Profil" avec form pré-rempli, bouton "Sauvegarder & régénérer cache"

#### `triskell_sales_tunnel/catalog.py`
Pas de modif lourde — juste un commentaire clarifiant que ces templates sont **founder-only** depuis v1.1.

## ⚙️ Détails techniques

### Cache invalidation
Quand profile change → invalidate tout le cache (`state.template_cache = {}`). Sinon les templates restent calés sur l'ancien profile.

### Key cache
```python
import hashlib
def _cache_key(product: str, client: str, channel: str, profile_hash: str) -> str:
    raw = f"{product}|{client}|{channel}|{profile_hash}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
```

`profile_hash` = sha1 d'une JSON-serialization stable du profile.

### UX onboarding
- Premier lancement : modal bloquante, ne ferme pas tant que les 5 questions non remplies
- Possible "Skip pour l'instant" qui met le mode founder OFF mais bloque la génération AI tant que profile non complet → message "Configure ton profil dans Settings"

### Mode founder
- Activé via env var `TRISKELL_FOUNDER=1` (à set par Jordan sur sa machine)
- Ou via fichier `.founder` dans le dossier user data
- Skip onboarding, charge les templates de `catalog.py`, désactive la génération AI

### Quel modèle par défaut ?
Garde claude-haiku-4-5 par défaut (déjà configuré). Recommandation : afficher dans Settings une note "Pour la qualité française, on recommande Claude Haiku ou GPT-4o-mini. Mistral et Grok sont supportés mais qualité variable en FR."

## 🧪 Tests

Ajouter dans `tests/` :
- `test_profile.py` : load/save UserProfile, validation, hash stable
- `test_ai_generate.py` : mocker urllib, vérifier que le prompt contient les bons placeholders
- `test_main_onboarding.py` : flow boot → onboarding → templates générés
- `test_cache.py` : hit/miss, invalidation au changement de profile

## 📦 Build

À la fin :
```bash
pyinstaller triskell_sales_tunnel.spec
# Smoke test : lancer le .exe, faire l'onboarding, générer 1 template
```

Vérifier que le bundle final reste dans la limite raisonnable (<10 Mo idéalement).

## 📋 Estimation

| Bloc | Temps |
|---|---|
| `profile.py` + dataclass + tests | 25 min |
| `OnboardingDialog` (5 écrans, validation) | 50 min |
| `generate_template()` + system prompt + parsing | 30 min |
| Cache local + invalidation | 25 min |
| Wiring `main.py` (onboarding flow + génération + cache) | 50 min |
| Settings → onglet "Profil" éditable | 30 min |
| Tests automatisés | 30 min |
| Build .exe + smoke validation | 20 min |
| **Total** | **~4h** |

## 🚦 Ordre d'attaque suggéré

1. Lire `main.py` (534 lignes) pour comprendre la structure UI / state
2. Lire `data.py` (162 lignes) pour comprendre la persistance
3. Lire `catalog.py` (juste les premiers 200 lignes) pour comprendre la structure templates
4. Coder `profile.py` (le plus simple)
5. Coder `OnboardingDialog` en isolé
6. Étendre `ai.py` avec `generate_template()`
7. Wirer le tout dans `main.py`
8. Settings tab profil
9. Tests + build

## 💰 Pricing décidé

Petit prix entre 9 et 14 € paiement unique (validé par Jordan). À implémenter dans les fichiers landing + Stripe checkout (séparés du code core de l'app).

## ✅ Définition de "fait"

- Premier lancement non-admin → onboarding s'ouvre, 5 questions complétées → templates générés via IA
- Profile éditable dans Settings → cache invalidé à la save
- Mode founder activé via `TRISKELL_FOUNDER=1` → skip onboarding, templates Triskell statiques
- Tests passent
- Build .exe fonctionne et fait <10 Mo

---

**Pour la session qui prend la relève** : commence par lire ce fichier, puis `main.py`, puis attaque dans l'ordre ci-dessus. Bon courage 🍻
