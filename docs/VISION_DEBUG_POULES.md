# Vision Debug — détection et sélection d'une poule

## Périmètre livré

Cette itération réutilise l'écran `Vision Debug` existant. Elle ajoute :

- la détection dédiée du template `chicken` ;
- l'affichage de toutes les candidates et de leur confiance ;
- la sélection de la meilleure candidate ;
- la conversion des coordonnées relatives à NosTale en coordonnées écran ;
- un clic réel protégé par la case `Armer le clic réel`.

## Préparation obligatoire du template

La détection ne peut pas être fiable sans image de référence issue du client NosTale de l'utilisateur.
Dans l'écran `Templates`, créer un template nommé exactement `chicken` en sélectionnant une petite zone caractéristique d'une poule visible dans le jeu. Éviter le sol, les ombres et les autres monstres.

Plusieurs templates de poses différentes pourront être ajoutés dans une itération suivante. La présente version attend un unique fichier `assets/templates/chicken.png`.

## Protocole de test

1. Placer le personnage dans la zone contenant les poules et les autres monstres.
2. Ouvrir `Vision Debug`.
3. Régler le seuil initial à `0.85` et la distance minimale à `40`.
4. Cliquer sur `Détecter les poules`.
5. Vérifier que les rectangles verts entourent uniquement de vraies poules.
6. Cocher `Armer le clic réel`.
7. Cliquer sur `Sélectionner la meilleure poule`.
8. Vérifier dans NosTale que la candidate choisie est réellement ciblée.

## Limites honnêtes

- aucune image de poule n'était fournie avec le dépôt ; la qualité réelle dépend donc du template créé dans le client de l'utilisateur ;
- la version ne confirme pas encore le nom de la cible dans l'interface NosTale ;
- elle n'attaque pas et ne lit pas les PV ;
- les poules partiellement masquées, animées ou affichées à une autre échelle peuvent nécessiter plusieurs templates ;
- le clic réel doit rester désarmé pendant les réglages du seuil afin d'éviter les actions involontaires.
