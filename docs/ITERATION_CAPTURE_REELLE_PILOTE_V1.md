# Itération — Capture réelle pilote V1

## Objectif

Valider la première action réellement envoyée à NosTale depuis la page Production : tenter de capturer une seule poule déjà préparée par l'utilisateur.

## Périmètre livré

- préflight de la fenêtre NosTale et de la configuration ;
- confirmation explicite avant toute entrée réelle ;
- envoi du raccourci `capture_new_pet` ;
- trois tentatives maximum ;
- vérification visuelle prudente dans la partie droite de la fenêtre, correspondant à la liste des familiers ;
- refus de démarrer si l'image de référence est instable ;
- journal des scores de stabilité et de changement ;
- aucun enchaînement XP, amélioration ou extraction en mode réel.

## Préparation manuelle requise

1. Ouvrir NosTale en mode fenêtré et afficher la liste des familiers.
2. Sélectionner une poule capturable.
3. L'affaiblir manuellement sous 50 % PV.
4. Vérifier dans Paramètres que le raccourci « Capturer un nouveau familier » correspond bien au jeu.
5. Dans Production, choisir `1` et `1★`, puis cliquer sur `Pilote réel : capturer 1 poule`.

## Critère de réussite

Le raccourci est envoyé et la liste des familiers change suffisamment après la tentative. L'application affiche alors « Capture confirmée ».

## Limites connues

Cette itération ne sait pas encore :

- détecter la poule sauvage ;
- lire précisément ses PV ;
- l'affaiblir sous 50 % ;
- distinguer avec certitude une capture réussie d'un autre changement visuel important dans la zone ;
- envoyer automatiquement la poule vers la réserve XP.

La validation dans le vrai client NosTale est indispensable avant de réutiliser ce signal dans l'orchestrateur complet.
