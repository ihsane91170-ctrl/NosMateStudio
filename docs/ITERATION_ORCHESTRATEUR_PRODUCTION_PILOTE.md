# Itération — Orchestrateur de production pilote

## Objectif

Fournir une première chaîne verticale fiable dans NosMate Studio : saisie d'une quantité et d'un niveau de jetons, calcul du plan, clic sur **Produire (simulation)**, déroulement des étapes, journal et progression jusqu'à 100 %.

## Périmètre livré

- planificateur récursif de jetons 1★ à 6★ ;
- écran **Production** intégré à la navigation existante ;
- orchestrateur avec états explicites ;
- journal des étapes : préflight, capture, réserve XP, XP, amélioration, extraction ;
- barre de progression ;
- demande d'arrêt ;
- verrouillage explicite du mode réel ;
- tests métier, orchestration et interface.

## Cycle pilote à tester

1. Lancer `python launcher.py`.
2. Ouvrir **Production**.
3. Choisir quantité `1`, niveau `1★`.
4. Cliquer sur **Produire (simulation)**.
5. Vérifier une progression à 100 % et la ligne `Objectif atteint : 1/1 jeton(s) 1★.`

## Limite assumée

Le mode réel n'est pas activé. Les interactions NosTale nécessitent encore des confirmations fiables et observables pour : PV sous 50 %, ratés, capture réussie, transfert en réserve, niveau atteint, amélioration réussie et extraction confirmée. Sans ces capteurs, un cycle réel pourrait dériver ou consommer des ressources sans preuve de succès.
