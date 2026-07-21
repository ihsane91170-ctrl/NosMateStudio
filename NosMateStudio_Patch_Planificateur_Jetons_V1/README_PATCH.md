# Patch NosMate Studio — Planificateur de production de jetons V1

## Installation

Décompresser ce patch à la racine du dépôt NosMate Studio en conservant les chemins. Le fichier `app/planning/__init__.py` remplace le fichier existant ; les autres fichiers sont ajoutés.

Sous PowerShell :

```powershell
Expand-Archive .\NosMateStudio_Patch_Planificateur_Jetons_V1.zip -DestinationPath .\patch
Copy-Item .\patch\* .\NosMateStudio\ -Recurse -Force
cd .\NosMateStudio
python -m pytest tests/test_production_planner.py -q
```

## Utilisation métier

```python
from app.planning import TokenProductionPlanner

plan = TokenProductionPlanner().plan(quantity=34, stars=3)

assert plan.token_quantity(1) == 102
assert plan.token_quantity(2) == 68
assert plan.token_quantity(3) == 34
assert plan.chickens_to_capture == 204
```

## Portée

Le patch ajoute le calcul métier et sa documentation. Il ne déclenche pas encore les workflows réels de capture, XP, amélioration ou extraction dans NosTale.
