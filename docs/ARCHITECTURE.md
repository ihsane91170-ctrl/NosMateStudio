# Architecture

## Modules

### `app/ui`

Affichage, saisie des paramètres et commandes utilisateur.

### `app/workflow`

Machine à états et orchestration fonctionnelle.

### `app/automation`

Interactions clavier et souris. Ce module ne prend aucune décision métier.

### `app/vision`

Détection de la fenêtre et reconnaissance visuelle des éléments du jeu.

### `app/config`

Configuration par défaut et configuration locale.

### `app/models`

États, objets métier et structures partagées.

### `app/services`

Journalisation et services transverses.

## Flux

```text
Utilisateur
    ↓
UI
    ↓
Workflow Engine
    ├── Vision Engine → observe
    ├── Automation Engine → agit
    ├── Configuration
    └── Logger
```

## Règles

1. Aucune touche ni coordonnée métier codée en dur.
2. Une action doit être suivie d'une vérification.
3. Le mode simulation est actif par défaut.
4. Les paramètres locaux ne sont pas versionnés.
5. Le workflow est indépendant de l'interface.
