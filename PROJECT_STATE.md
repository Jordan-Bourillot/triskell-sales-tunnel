# PROJECT_STATE — Triskell Sales Tunnel

## Phase courante
Phase 11 — Build .exe (TERMINÉE — toutes phases livrées)

## Phases terminées
- Phase 0 — Bootstrap (arborescence, deps, state)
- Phase 1 — Livrable 1 : Structure commerciale (4 niveaux)
- Phase 2 — Catalogue de données (produits / clients / canaux / templates)
- Phase 3 — Thème & branding (palette, polices, logo Triskell vectoriel)
- Phase 4 — Moteur de templates (placeholders, régénération, sanitisation)
- Phase 5 — UI Wizard (4 étapes + indicateur + transitions)
- Phase 6 — Export / copie / persistance utilisateur
- Phase 7 — Tests automatisés + README + lancement
- Phase 8 — Spec & script PyInstaller
- Phase 9 — Exporters PDF / DOCX (reportlab + python-docx)
- Phase 10 — Intégration IA Claude / OpenAI + Settings dialog
- Phase 11 — Build .exe Windows autonome (6.9 MB, smoke validé)

## Stack
- Python 3.10+
- customtkinter 5.2+
- Pillow (logo + assets)
- pyperclip (copie système robuste, fallback tkinter inclus)
- reportlab (export PDF brandé Triskell)
- python-docx (export Word)
- urllib.request (appels IA, stdlib pure — zéro dep)
- pytest (tests)
- pyinstaller (build .exe, dev only)

## Variables d'env requises
Aucune — l'app est 100 % offline.
Optionnel : `TRISKELL_DATA_DIR` pour rediriger les données utilisateur.

## Schéma persistance utilisateur
Fichier JSON : `%APPDATA%/TriskellSalesTunnel/user_state.json`
```
{
  "custom_products": [...],
  "custom_clients": [...],
  "last_values": { "prenom": "...", "nom_entreprise": "..." },
  "history": [ { "ts": "...", "product": "...", "client": "...", "channel": "..." } ]
}
```

## Fichiers structurants
- `triskell_sales_tunnel/main.py` — entrypoint app + boucle CTk
- `triskell_sales_tunnel/theme.py` — tokens design (couleurs, typo, espacements)
- `triskell_sales_tunnel/data.py` — chargement catalogue + state utilisateur
- `triskell_sales_tunnel/catalog.py` — produits/clients/canaux/templates (statique)
- `triskell_sales_tunnel/template_engine.py` — moteur placeholders + variantes
- `triskell_sales_tunnel/widgets/triskell_logo.py` — logo triskell vectoriel
- `triskell_sales_tunnel/widgets/step_indicator.py` — indicateur de progression
- `triskell_sales_tunnel/widgets/components.py` — boutons / cards / chips réutilisables
- `triskell_sales_tunnel/steps/` — 4 écrans (produit, client, canal, template)

## Décisions structurantes
- Stack Python + CustomTkinter (brief : "le plus simple et léger") plutôt que Tauri.
- Mode sombre par défaut, toggle clair disponible.
- Logo triskell dessiné en vectoriel via Canvas (zéro asset binaire requis, scale parfait).
- Templates stockés en Python pur (catalog.py) → typage strict, recherche rapide, diff Git lisible.
- Placeholders affichés `[Prénom]` (lisible) et stockés `{prenom}` (interne).
- État utilisateur dans %APPDATA% (Windows) / `~/.config` (POSIX).

## TODOs reportés (BACKLOG.md)
Voir BACKLOG.md.
