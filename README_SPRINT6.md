# NosMate Studio — Sprint 6

## Fonction livrée

Chaîne réelle unique et sécurisée :

1. détection IA ;
2. sélection de la meilleure poule ;
3. clic réel ;
4. nouvelle capture ;
5. revalidation spatiale de la même poule ;
6. attaque avec la touche configurée ;
7. arrêt.

L'attaque n'est jamais envoyée lorsque la cible ne peut pas être confirmée après le clic.

## Interface

Dans **Vision Debug** :

- régler le seuil IA, par exemple `0,25` ;
- régler la touche d'attaque, par défaut `1` ;
- régler le délai clic → validation, par défaut `0,15 s` ;
- cocher **Armer le clic réel** ;
- cliquer sur **Sélectionner et attaquer**.

Le journal affiche les états :

`SEARCH_TARGET → TARGET_FOUND → CLICK_TARGET → VALIDATE_TARGET → TARGET_CONFIRMED → ATTACK → FINISHED`

## Tests

```powershell
python -m pytest tests/test_action_engine.py tests/test_target_attack.py tests/test_ai_target_selector.py tests/test_vision_debug_ai_selection.py -q
```

Les tests métier non-Qt ont été exécutés dans l'environnement de livraison : `12 passed`.
Les tests Qt n'ont pas pu être exécutés dans cet environnement Linux car PySide6 n'y est pas installé. La compilation Python de l'ensemble des fichiers modifiés a réussi.

## Limite volontaire

Ce sprint ne lit pas encore la barre de vie et ne capture pas la poule. Il envoie une seule attaque puis s'arrête.
