# Triskell Sales Tunnel

> Application desktop premium pour générer en 4 clics le bon message de prospection,
> sur le bon canal, pour le bon client.
> Made in Bretagne par **Triskell Studio**.

---

## Aperçu

- **Tunnel à 4 étapes** : Produit → Client cible → Canal → Template final.
- **31 cibles** pré-priorisées sur **6 produits** Triskell.
- **~50 templates rédigés à la main**, courts, chaleureux et professionnels.
- **Placeholders révélables** (`[Prénom]`, `[Nom entreprise]`, ...) avec champs de saisie.
- **Bouton régénérer** qui adapte le texte aux valeurs saisies.
- **Copie 1 clic** + **export `.txt` / `.pdf` / `.docx`** (PDF et DOCX brandés Triskell).
- **Reformulation IA** via Claude (Anthropic) ou OpenAI — bouton ✨.
- **Mode sombre par défaut**, mode clair en 1 clic.
- **Logo triskell vectoriel**, palette officielle Triskell Studio.
- **Build .exe Windows autonome** via PyInstaller.
- **100% offline par défaut** ; appels IA uniquement vers le provider que tu choisis.

---

## Stack

- Python 3.10+
- [`customtkinter`](https://customtkinter.tomschimansky.com/) 5.2+
- `Pillow` (assets)
- `pyperclip` (copie système, fallback Tk natif)
- `pytest` (tests)

---

## Installation

```bash
# 1. Cloner / récupérer le dossier `Prospection`
cd Prospection

# 2. (Recommandé) créer un venv
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Lancer l'application

```bash
# Méthode 1 — script racine
python run.py

# Méthode 2 — module
python -m triskell_sales_tunnel
```

---

## Lancer les tests

```bash
python -m pytest
```

Tous les tests passent (41 cas) — moteur de templates, catalogue, persistance.

---

## Personnalisation

### Ajouter / modifier un template

Édite [`triskell_sales_tunnel/catalog.py`](triskell_sales_tunnel/catalog.py).
La structure est typée et auto-validée par les tests :

```python
ChannelTemplate(
    channel="email",
    subject="Mon objet personnalisé",
    body="Bonjour {prenom}, ...",
)
```

Lance `pytest` après modification — les tests vérifient que :
- Toute clé est unique.
- Tout email a un objet.
- Aucun corps n'est vide.
- Tous les placeholders sont humanisables.

### Ajouter un produit / une cible custom *à chaud*

Bouton `+ Ajouter un produit personnalisé` (étape 1) ou `+ Ajouter une cible personnalisée` (étape 2).
Stocké dans `%APPDATA%\TriskellSalesTunnel\user_state.json`.

### Changer la palette / le logo

[`triskell_sales_tunnel/theme.py`](triskell_sales_tunnel/theme.py) regroupe **toutes** les couleurs et les typos.
Le logo est dessiné vectoriellement dans [`triskell_sales_tunnel/widgets/triskell_logo.py`](triskell_sales_tunnel/widgets/triskell_logo.py).

---

## Architecture

```
Prospection/
├─ run.py                          # entrypoint racine
├─ requirements.txt
├─ pytest.ini
├─ STRUCTURE_COMMERCIALE.md        # Livrable 1 (rédigé)
├─ PROJECT_STATE.md                # journal projet
├─ BACKLOG.md                      # idées hors scope
├─ triskell_sales_tunnel/
│  ├─ main.py                      # TriskellApp + WizardSession
│  ├─ theme.py                     # tokens couleur, typo, espacements
│  ├─ catalog.py                   # produits / clients / templates
│  ├─ data.py                      # persistance utilisateur (JSON)
│  ├─ template_engine.py           # placeholders + rendu
│  ├─ widgets/
│  │   ├─ triskell_logo.py         # logo vectoriel
│  │   ├─ step_indicator.py        # barre 4 étapes
│  │   └─ components.py            # cartes / chips / boutons
│  └─ steps/
│      ├─ step_product.py
│      ├─ step_client.py
│      ├─ step_channel.py
│      └─ step_template.py
└─ tests/
   ├─ test_template_engine.py
   ├─ test_catalog.py
   └─ test_data.py
```

---

## Données utilisateur

L'app stocke tes valeurs préférées (prénom, nom d'entreprise par défaut, etc.) et l'historique des templates générés dans :

| OS      | Chemin                                              |
|---------|------------------------------------------------------|
| Windows | `%APPDATA%\TriskellSalesTunnel\user_state.json`     |
| macOS   | `~/.config/TriskellSalesTunnel/user_state.json`     |
| Linux   | `$XDG_CONFIG_HOME/TriskellSalesTunnel/user_state.json` |

Tu peux forcer un autre dossier avec la variable d'environnement `TRISKELL_DATA_DIR`.

---

## Build .exe Windows autonome

Le projet inclut un script de build clé en main basé sur **PyInstaller** :

```bash
python build_exe.py
```

Ce script :
1. Installe PyInstaller s'il manque,
2. Nettoie les anciens dossiers `build/` et `dist/`,
3. Lance le build via [`triskell_sales_tunnel.spec`](triskell_sales_tunnel.spec) (mode `onedir`),
4. Affiche le chemin et la taille du binaire produit.

Résultat :

```
dist/Triskell Sales Tunnel/
├─ Triskell Sales Tunnel.exe   ← double-clic pour lancer
├─ ... (DLL Python + tk + customtkinter)
```

Distribuer = zipper le dossier `dist/Triskell Sales Tunnel/`.

## Reformulation IA

L'app intègre un bouton **✨ Reformuler IA** dans l'écran final qui appelle :
- **Anthropic Claude** (par défaut, modèle `claude-haiku-4-5`)
- ou **OpenAI** (modèle `gpt-4o-mini` par défaut)

### Configuration

1. Clique sur **⚙ Paramètres** (header)
2. Choisis ton fournisseur
3. Colle ta clé API
4. (Optionnel) personnalise le modèle

Alternative recommandée — variables d'environnement (priorité absolue, jamais persistées) :

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# ou
$env:OPENAI_API_KEY = "sk-..."
python run.py
```

### Sécurité

- Les clés saisies dans Paramètres sont **obfusquées** (XOR + base64) dans `user_state.json` — c'est mieux que rien mais **ce n'est pas du chiffrement fort**. Pour un usage pro, privilégie les variables d'env.
- Aucun appel réseau hors du provider que tu choisis explicitement.
- Le prompt préserve les placeholders `[Comme Ceci]` à l'identique.

---

© Triskell Studio — Bretagne, 2026.
