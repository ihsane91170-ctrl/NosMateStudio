# Sprint 6.1 — Tentatives d'attaque bornées

Ce correctif remplace l'attaque unique par 1 à 5 tentatives configurables.

Séquence :

1. détecter et cliquer la meilleure poule ;
2. attendre la prise en compte de la sélection ;
3. revalider visuellement la cible ;
4. envoyer une tentative d'attaque ;
5. attendre ;
6. avant toute nouvelle tentative, revalider la cible ;
7. arrêter immédiatement si la cible disparaît ;
8. ne jamais lancer de capture dans ce workflow.

Réglages conseillés pour le premier essai :

- délai clic → validation : 0,40 s ;
- tentatives maximum : 2 ;
- délai entre tentatives : 0,70 s.

Important : tant que la lecture des PV ou un indicateur fiable de dégâts n'est pas intégrée, le logiciel ne peut pas certifier qu'un coup a touché. Il borne les tentatives et vérifie seulement que la cible est encore présente avant de recommencer.
