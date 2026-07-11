# Sprint 1 — MVP Préparation de session

## Objectif

Permettre à l'utilisateur de lancer un workflow complet jusqu'à l'affectation des trois premiers familiers.

## Démonstration attendue

```text
START
→ NosTale détecté
→ Capture X
→ Téléportation
→ Invocation faible / normale / forte
→ Affectation familier 1
→ Affectation familier 2
→ Affectation familier 3
→ Session prête
```

## Definition of Done

- Le parcours de bout en bout fonctionne en mode simulation.
- Le parcours fonctionne en environnement réel après calibration.
- Pause, arrêt et arrêt d'urgence sont disponibles.
- Les erreurs sont journalisées.
- Les critères d'acceptation des US du sprint sont validés.
- Les tests automatisés passent.
- La Pull Request `develop` vers `main` est validée.

## Risques

- État de l'interface variable.
- Lag et temps de chargement non constants.
- Fenêtre déplacée ou redimensionnée.
- Clic non pris en compte.
- Capture échouée sans détection.
