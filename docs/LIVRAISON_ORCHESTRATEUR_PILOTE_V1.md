# Livraison — Orchestrateur de production pilote V1

## Objectif

Transformer le plan calculé en une exécution suivie, interrompable et observable, sans prétendre que les interactions réelles avec NosTale sont déjà fiables.

## Fonctionnalités livrées

- bouton **Produire** sur l'écran Planificateur ;
- mode simulation de la chaîne capture → réserve XP → leveling → amélioration → extraction ;
- barre de progression et journal des étapes ;
- résultat final produit/demandé ;
- arrêt demandé pris en compte à la prochaine frontière d'étape ;
- mode réel explicitement verrouillé ;
- orchestrateur indépendant de Qt et testable hors Windows.

## Cycle pilote recommandé

`1 jeton 1★` : une poule, niveau 10, extraction, compteur final 1/1.

## Non livré dans cette itération

- clics réels dans NosTale ;
- lecture fiable des PV sous 50 % ;
- confirmation d'attaque ratée ou réussie ;
- confirmation de capture ;
- détection réelle du niveau et des étoiles ;
- amélioration et extraction réelles ;
- arrêt instantané au milieu d'une action bloquante.

Ces éléments exigent Windows, une fenêtre NosTale active et des calibrations visuelles spécifiques au client de l'utilisateur.
