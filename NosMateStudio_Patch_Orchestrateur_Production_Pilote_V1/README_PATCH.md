# NosMate Studio — Orchestrateur de production pilote V1

## Installation

Copier le contenu de ce dossier à la racine du dépôt NosMate Studio et accepter la fusion des dossiers.

## Validation

```powershell
python -m pytest tests/test_production_planner.py tests/test_production_orchestrator.py -q
```

Résultat attendu : `22 passed`.

Pour tester l'interface sous Windows :

```powershell
python -m pytest tests/test_production_planner_page.py -q
python launcher.py
```

Dans **Planificateur** :

1. choisir `1` et `1★` ;
2. laisser le mode `Simulation` ;
3. cliquer sur `Produire` ;
4. vérifier une progression jusqu'à 100 % et le statut `1/1`.

Le mode réel est volontairement verrouillé. Il ne sera activé qu'après validation des confirmations visuelles de capture, niveau, amélioration et extraction sous NosTale.
