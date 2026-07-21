# Livraison — Interface du planificateur de jetons V1

## Objectif

Permettre à l'utilisateur de choisir une quantité et un niveau de jetons depuis NosMate Studio, puis d'afficher immédiatement le plan de production calculé.

## Fonctionnement livré

Une nouvelle entrée **Planificateur** est ajoutée à la navigation principale.

L'écran permet de saisir :

- une quantité comprise entre 1 et 999 999 ;
- un niveau de jeton compris entre 1★ et 6★.

Le bouton **Calculer le plan** affiche :

- l'objectif demandé ;
- le nombre total de poules à capturer ;
- chaque lot de jetons intermédiaires ;
- le niveau d'extraction correspondant à chaque étoile ;
- la distinction entre jetons intermédiaires et jetons finaux.

## Cas de référence

Pour 34 jetons 3★ :

- 102 jetons 1★ au niveau 10 ;
- 68 jetons 2★ au niveau 20 ;
- 34 jetons 3★ au niveau 30 ;
- 204 poules à capturer au total.

## Limite actuelle

L'écran calcule et présente le plan. Il ne déclenche pas encore les workflows réels de capture, XP, amélioration et extraction dans NosTale.
