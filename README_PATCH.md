# Patch S9 — Page Production

Copier le contenu du dossier à la racine de NosMateStudio.

## Intégration MainWindow

Le patch contient une version de `app/ui/main_window.py` intégrant la nouvelle entrée `Production` dans la barre latérale.

## Tests

```powershell
python -m pytest tests/test_token_production_planner.py tests/test_production_page.py -q
```

## Portée réelle

- calcul métier : opérationnel ;
- interface : opérationnelle ;
- capture réelle depuis cette page : non branchée ;
- XP, augmentation d'étoiles et extraction : non branchés.
