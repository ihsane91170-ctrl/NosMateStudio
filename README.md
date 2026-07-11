# NosMate Studio

Application Windows de préparation automatisée d'une session d'entraînement NosMate.

> Statut : **v0.1.0-alpha — Sprint 0**

## Vision

NosMate Studio automatise un workflow répétitif :

1. Capturer un nombre défini de familiers.
2. Utiliser l'objet de téléportation vers la zone où ils sont regroupés.
3. Invoquer trois protomonstres.
4. Sélectionner les trois premiers familiers.
5. Cliquer sur **Accompagner**.
6. Affecter chaque familier à une cible :
   - Familier 1 → Protomonstre faible
   - Familier 2 → Protomonstre
   - Familier 3 → Protomonstre fort
7. Confirmer que la préparation est terminée.

## Architecture cible

```text
UI
│
└── Workflow Engine
    ├── Automation Engine
    ├── Vision Engine
    ├── Configuration
    └── Journalisation
```

## Installation développeur

Prérequis : Python 3.11 ou 3.12 et Git.

```bash
git clone https://github.com/ihsane91170-ctrl/NosMateStudio.git
cd NosMateStudio

py -m venv .venv
.venv\Scripts\activate

py -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Lancer l'application

```bash
python launcher.py
```

## Lancer les tests

```bash
pytest
```

## Qualité

```bash
ruff check .
ruff format .
```

## Branches

- `main` : versions validées
- `develop` : intégration du sprint
- `feature/USxxx-description` : une branche par User Story

Voir [CONTRIBUTING.md](CONTRIBUTING.md) et [docs/BACKLOG.md](docs/BACKLOG.md).

## Licence

Aucune licence publique n'est attribuée pour le moment. Le dépôt reste privé et tous les droits sont réservés.
