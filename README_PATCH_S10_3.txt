Patch S10.3 — Retour zone XP après lot + confirmation Entrée

Corrections :
1. Toutes les poules demandées sont capturées dans la zone avant le retour XP.
2. Le retour XP n'est lancé qu'une seule fois, après la dernière capture confirmée.
3. Après la touche de retour configurée, Entrée est envoyée pour confirmer.

Installation : extraire à la racine de NosMateStudio et remplacer les fichiers.

Tests :
python -m pytest tests/test_capture_batch_controller.py tests/test_hotkey_return_to_exp_zone.py -q
