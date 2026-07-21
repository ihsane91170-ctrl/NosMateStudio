# S10.1 — Diagnostic capture depuis Production

Ce correctif traite le cas où l'IHM affiche `Capture 1/1` sans action visible dans NosTale.

## Changements

- activation explicite de la fenêtre NosTale avant l'analyse IA et les entrées ;
- le statut de la page Production affiche maintenant la vraie cause de chaque tentative échouée ;
- exemples : fenêtre impossible à activer, aucune poule sélectionnable, modèle IA indisponible, erreur attaque/capture ;
- le compteur n'est plus présenté comme une capture réussie : il indique qu'une tentative est en cours.

## Validation

- compilation Python des fichiers modifiés : OK ;
- tests du contrôleur de lot : 4 réussis ;
- tests Qt non exécutés dans l'environnement de génération, PySide6 absent.
