# Patch S10.2 — Pipeline partagé Vision Debug / Production

## Objectif

Le bouton Production utilise désormais les mêmes instances que Vision Debug pour :

- la fenêtre NosTale ;
- la capture écran ;
- le modèle YOLO ;
- le sélecteur de cible ;
- la souris réelle ;
- le lecteur de PV ;
- le service attaque/capture.

Le seuil IA de Production est aligné sur le seuil actuellement validé dans Vision Debug : `0.80`.

## Installation

Copier le contenu du ZIP à la racine de NosMate Studio et accepter les remplacements.
Relancer complètement l'application.

## Test

1. Ouvrir Vision Debug et vérifier que « Détecter par IA » trouve une poule.
2. Sans fermer l'application, ouvrir Production.
3. Demander une seule poule et cliquer sur « Lancer la capture ».

La souris doit maintenant se déplacer vers la cible retenue, puis lancer la séquence attaque/capture.
