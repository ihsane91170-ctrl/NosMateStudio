# ADR-008 — Traduire les raccourcis selon la disposition du clavier

## Statut

Accepté

## Contexte

PyDirectInput utilise des positions physiques proches d’un clavier QWERTY.

Sur un clavier AZERTY :

- `q` envoyé physiquement produit `a` ;
- `a` envoyé physiquement produit `q` ;
- certaines touches de ponctuation sont ambiguës.

## Décision

L’utilisateur configure les touches telles qu’elles apparaissent dans
NosTale.

Un KeyboardLayoutTranslator les convertit avant l’appel à PyDirectInput.

## Conséquences

- l’interface reste compréhensible ;
- le runtime gère les différences de disposition ;
- d’autres dispositions pourront être ajoutées ;
- les symboles complexes restent à éviter dans le MVP.