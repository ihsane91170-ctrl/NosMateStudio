NosMate Studio — Patch S10.7 Sélection sécurisée multi-images

Installation :
- extraire le contenu de ce ZIP à la racine du projet ;
- accepter le remplacement des fichiers ;
- relancer complètement NosMate Studio.

Comportement :
- 3 captures IA successives avant tout clic réel ;
- cible retrouvée sur au moins 2 images ;
- confiance minimale de 0,90 pour une action réelle ;
- rejet si une détection not_chicken chevauche la cible ;
- en cas de doute : aucun clic, aucune attaque.

Le faux positif fourni à 0,887 est désormais bloqué par le verrou de sécurité.

Tests :
python -m pytest tests/test_temporal_target_validator.py -q
