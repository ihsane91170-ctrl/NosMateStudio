# S10 — Branchement réel du bouton Capture

## Fonctionnel

Le bouton **Production > Lancer la capture** pilote maintenant réellement :

1. détection de la fenêtre NosTale ;
2. détection IA d'une poule ;
3. sélection de la meilleure cible ;
4. attaque jusqu'à 1 PV ;
5. capture avec retry ;
6. envoi de la touche configurée `go_to_pet_xp_zone` ;
7. progression et arrêt depuis l'interface.

L'exécution se fait dans un `QThread`, donc l'interface ne se fige pas.

## Limite connue

Le trajet **zone XP -> zone de capture** n'est pas encore implémenté, car aucune action/calibration dédiée n'existe dans le projet. Par conséquent, un lot supérieur à 1 ne pourra continuer que si le personnage revient déjà automatiquement dans une zone contenant des poules après la touche de retour.

## Tests validés dans l'environnement de livraison

```text
13 passed
```

Tests métier exécutés : contrôleur de lot, attaque/capture et planificateur.
Les tests Qt n'ont pas été exécutés dans l'environnement de livraison faute de PySide6 installé.
