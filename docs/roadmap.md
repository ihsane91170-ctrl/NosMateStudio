# NosMate Studio — Roadmap

## Objectif produit

NosMate Studio automatise la gestion et la montée en expérience des
familiers dans NosTale grâce à :

- un moteur de workflows ;
- des exécuteurs clavier, souris et attente ;
- un mode simulation et un mode réel ;
- une détection visuelle basée sur des templates ;
- une logique métier dédiée aux familiers.

## État global

| Epic | État |
|---|---|
| EPIC-01 — Vision | En cours |
| EPIC-02 — Gestion des familiers | En cours |
| EPIC-03 — OCR | À faire |
| EPIC-04 — XP | À faire |
| EPIC-05 — Fusion | À faire |
| EPIC-06 — Capture | À faire |
| EPIC-07 — Scheduler | À faire |

## Livrable 1 — MVP technique

- [x] Interface PySide6
- [x] Configuration des raccourcis
- [x] Calibration
- [x] Workflow Engine
- [x] Runtime simulation
- [x] Runtime réel
- [x] Preflight
- [x] Traduction AZERTY vers touches physiques
- [x] Capture de la fenêtre NosTale
- [x] Éditeur de templates
- [x] Template matching OpenCV
- [x] VisionService
- [x] Sélection visuelle d’un familier
- [x] Recherche du bouton Accompagner

## Livrable 2 — Bot métier

- [ ] Détecter tous les familiers visibles
- [ ] Parcourir les familiers
- [ ] Lire le niveau
- [ ] Lire le nombre d’étoiles
- [ ] Sélectionner les familiers à entraîner
- [ ] Exécuter un cycle XP complet
- [ ] Répéter les cycles jusqu’à l’objectif

## Livrable 3 — Fiabilité et distribution

- [ ] Retry et timeouts
- [ ] Arrêt utilisateur réellement réactif
- [ ] Historique des exécutions
- [ ] Statistiques
- [ ] Packaging Windows
- [ ] Documentation utilisateur
- [ ] Release stable