# Séparation Capture / Production de familiers

## Partie 1 — CaptureBatchController

Responsabilité unique : capturer le nombre de poules demandé et revenir dans la zone
d'XP après chaque capture confirmée, y compris après la dernière du lot.

Cette partie ne connaît ni les protomonstres, ni les étoiles, ni l'extraction.

## Partie 2 — FamiliarProductionController

Responsabilité unique : transformer les familiers déjà capturés :

1. accompagner et entraîner jusqu'au niveau maximum de l'étoile courante ;
2. augmenter l'étoile lorsque l'objectif est supérieur ;
3. réentraîner après chaque augmentation, puisque le niveau retombe à 1 ;
4. extraire le jeton lorsque l'étoile cible est atteinte au niveau maximum.

Cette partie ne déclenche jamais une capture de poule sauvage.

## Prochaine intégration

Les contrôleurs sont indépendants des clics et de la vision. Les services réels devront
adapter les briques déjà validées : détection IA, attaque/capture, déplacement, sélection
des familiers, protomonstres, augmentation d'étoile et extraction.
