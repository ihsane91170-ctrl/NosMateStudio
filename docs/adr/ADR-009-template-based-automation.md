# ADR-009 — Privilégier les templates aux coordonnées fixes

## Statut

Accepté

## Contexte

Les coordonnées fixes deviennent incorrectes lorsque :

- la fenêtre est déplacée ;
- la résolution change ;
- un panneau est repositionné ;
- l’interface évolue légèrement.

## Décision

Utiliser des templates visuels pour localiser les éléments interactifs
lorsque cela est possible.

Les coordonnées fixes restent réservées aux cas où aucune ancre visuelle
fiable n’existe.

## Conséquences

- meilleure robustesse ;
- nécessité de maintenir une bibliothèque de templates ;
- dépendance à la qualité des captures ;
- besoin de seuils et de stratégies de déduplication.