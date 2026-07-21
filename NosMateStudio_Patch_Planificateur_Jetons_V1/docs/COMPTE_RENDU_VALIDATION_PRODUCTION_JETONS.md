# Compte rendu de validation — Planificateur de production de jetons

## Éléments testés dans l'environnement de livraison

- import du module métier sans PySide6, Windows ni NosTale ;
- calcul de l'objectif 34 jetons 3★ : 102 jetons 1★, 68 jetons 2★, 34 jetons 3★ et 204 poules ;
- objectif 1★ sans amélioration intermédiaire ;
- objectif de quantité nulle ;
- chaîne complète jusqu'à 6★ ;
- plafonds des poules `10 × étoiles` ;
- plafonds des protomonstres faible 20, normal 40 et fort 60 ;
- rejet des quantités et niveaux invalides ;
- non-régression via la suite de tests existante du dépôt, dans la limite des dépendances disponibles.

## Éléments non testables sans Windows et NosTale

- détection de la fenêtre NosTale et comportement en cas de réduction/redimensionnement ;
- lecture fiable des PV et confirmation du seuil inférieur à 50 % ;
- distinction entre attaque réussie et attaque ratée ;
- confirmation visuelle d'une capture et gestion d'un échec ;
- envoi réel de chaque poule vers la réserve XP ;
- invocation et amorçage réel des trois protomonstres ;
- confirmation que chaque poule est correctement ciblée ;
- lecture fiable du niveau et du nombre d'étoiles ;
- amélioration réelle, contrôle du coût consommé et retour au niveau 1 ;
- extraction uniquement au niveau maximal et confirmation du jeton obtenu ;
- robustesse aux latences, changements d'interface, résolutions et pertes de focus.

## Conclusion

Le planificateur est déterministe et testable hors jeu. Il constitue le calcul de référence à brancher sur l'interface et les workflows existants. La présente livraison ne certifie pas l'automatisation réelle des actions NosTale.
