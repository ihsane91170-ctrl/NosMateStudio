# Livraison — sélection fiable d'un familier

Cette livraison cible le blocage observé dans `Chicken Accompany Test` :
le template est détecté, mais le clic ne sélectionne pas toujours le familier.

## Corrections apportées

- activation automatique de la fenêtre NosTale avant chaque clic réel ;
- conversion DPI entre les pixels de la capture et les coordonnées écran ;
- clic au centre réel du template détecté ;
- trois tentatives de sélection avec observation après chaque clic ;
- captures de diagnostic numérotées dans `captures/` ;
- vérification après le clic sur `Accompagner` ;
- dépendances d'exécution complétées dans `pyproject.toml`.

## Installation

Dans PowerShell, à la racine du projet :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
python launcher.py
```

L'activation du venv est facultative. Alternative :

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe launcher.py
```

## Test dans NosTale

1. Afficher la liste des familiers à droite.
2. Choisir `Chicken Accompany Test`.
3. Choisir le mode `Réel`, un cycle.
4. Démarrer sans sélectionner une poule manuellement.

## Diagnostics produits

- `captures/chicken_workflow_capture.png` : capture avant sélection ;
- `captures/chicken_click_position.png` : rectangle rouge et point vert du clic ;
- `captures/chicken_after_click_1.png` à `_3.png` : état après chaque tentative ;
- `captures/chicken_after_accompany.png` : vérification finale.

Si l'action échoue encore, `chicken_click_position.png` et la dernière capture
`chicken_after_click_N.png` suffisent pour déterminer précisément la suite.
