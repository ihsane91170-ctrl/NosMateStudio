# Protocole de validation S4

## Critère principal

Un autre monstre ressemblant à une poule doit être affiché en rouge et ne doit jamais être sélectionnable.

## Lecture des scores

- `poule` : meilleure confiance obtenue par un template `chicken*`.
- `autre` : meilleure confiance locale obtenue par un template `not_chicken*`.
- `marge` : `poule - autre`.
- acceptation : marge supérieure ou égale à la marge minimale.

## Réglage conseillé

Commencer avec :

- seuil poule : `0.80` ;
- seuil autre : `0.45` ;
- marge minimale : `0.12`.

Si un faux positif reste vert, créer un template négatif plus précis à partir de ce monstre ou augmenter la marge minimale par pas de `0.03`.

Si les vraies poules deviennent rouges, ajouter d'autres frames `chicken_02`, `chicken_03` plutôt que de réduire fortement la marge.
