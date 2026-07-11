# ADR-007 — Utiliser un VisionService

## Statut

Accepté

## Contexte

Les premières actions visuelles dépendaient directement du fournisseur de
captures, du matcher et de la fenêtre du jeu.

Cela dupliquait la logique dans plusieurs actions.

## Décision

Encapsuler les opérations visuelles dans un VisionService.

Le service expose notamment :

- `capture()`
- `find()`
- `exists()`
- `click()`
- prochainement `find_all()`

## Conséquences

### Positives

- les actions restent lisibles ;
- OpenCV n’est pas importé dans les workflows ;
- les dépendances sont centralisées ;
- les tests utilisent un unique faux service.

### Négatives

- une abstraction supplémentaire doit être maintenue ;
- certaines opérations avancées nécessiteront d’enrichir l’API.