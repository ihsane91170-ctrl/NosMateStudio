NosMate Studio — Patch S10.8
Séparation des compteurs Recherche IA / Capture réelle

Installation :
1. Fermer NosMate Studio.
2. Extraire ce ZIP à la racine du projet.
3. Accepter le remplacement des fichiers.
4. Relancer l'application.

Nouveau comportement :
- Une cible rejetée par la sécurité IA incrémente uniquement le compteur de recherche.
- Elle ne consomme plus l'une des 10 tentatives de capture.
- 100 recherches IA maximum sont autorisées par poule.
- 10 cycles de capture réels maximum sont conservés par poule.
- L'IHM affiche séparément recherches et captures réelles.

Tests :
python -m pytest tests/test_capture_batch_controller.py tests/test_hotkey_return_to_exp_zone.py -q
Résultat attendu : 12 passed
