# NosMate Studio — Spécification métier consolidée de production de jetons

## 1. Objectif produit

L'utilisateur saisit une quantité `N` et un niveau de jeton `K`, par exemple **34 jetons 3★**. NosMate Studio calcule les poules et jetons intermédiaires à produire, puis fournit le plan d'exécution allant de la capture à l'extraction.

Cette livraison couvre le calcul métier. L'automatisation réelle reste soumise à la reconnaissance fiable de l'état du client NosTale.

## 2. Règles de référence

### 2.1 Capture

1. Sélectionner une poule sauvage disponible.
2. L'affaiblir jusqu'à ce que ses PV soient strictement inférieurs à 50 %.
3. Après chaque attaque, vérifier si l'action a raté et réessayer tant que le seuil n'est pas confirmé.
4. Déclencher la capture uniquement lorsque le seuil de PV est confirmé.
5. Vérifier que la capture a réussi. En cas d'échec, reprendre le cycle sur la même cible si elle est encore valide, sinon sélectionner une nouvelle poule.
6. Envoyer chaque poule capturée vers la réserve XP avant de poursuivre la production.

Le compteur de poules capturées n'est incrémenté qu'après confirmation de la capture et de l'envoi vers la réserve XP.

### 2.2 Réserve XP et amorçage initial

Le système prépare au maximum trois poules simultanément. Au début d'un lot XP :

1. invoquer un protomonstre faible ;
2. invoquer un protomonstre normal ;
3. invoquer un protomonstre fort ;
4. sélectionner la première poule, cliquer sur « Accompagner », puis lui faire porter le premier coup sur le protomonstre faible ;
5. répéter avec la deuxième poule sur le protomonstre normal ;
6. répéter avec la troisième poule sur le protomonstre fort.

Cet amorçage initial est obligatoire afin que chaque protomonstre cible le familier prévu. Les poules suivantes peuvent être engagées selon le workflow calibré, mais le système doit toujours confirmer que la poule sélectionnée participe bien au combat.

### 2.3 Plafonds des protomonstres

| Protomonstre | Niveau maximal pris en charge |
|---|---:|
| Faible | 20 |
| Normal | 40 |
| Fort | 60 |

Le plan d'exécution doit choisir un protomonstre capable d'accompagner la poule jusqu'à son plafond courant. Le planificateur livré expose ces plafonds comme constantes métier, sans piloter encore le choix réel en jeu.

### 2.4 Plafond des poules

Le niveau maximal d'une poule est :

`niveau maximal = 10 × nombre d'étoiles`

Exemples : 1★ → niveau 10 ; 2★ → niveau 20 ; 3★ → niveau 30 ; 6★ → niveau 60.

### 2.5 Amélioration d'étoile

Coût pour améliorer une poule :

| Passage | Jetons nécessaires |
|---|---:|
| 1★ → 2★ | 1 jeton 1★ |
| 2★ → 3★ | 2 jetons 2★ |
| 3★ → 4★ | 3 jetons 3★ |
| 4★ → 5★ | 3 jetons 4★ |
| 5★ → 6★ | 4 jetons 5★ |

Après chaque amélioration réussie, la poule revient au **niveau 1**. Son XP doit donc être recommencée jusqu'au nouveau plafond avant l'étape suivante.

L'amélioration ne doit être comptabilisée qu'après confirmation visuelle du nouveau nombre d'étoiles et du retour au niveau 1.

### 2.6 Extraction

Une poule destinée à produire un jeton `K★` est extraite seulement lorsque :

- elle possède exactement `K` étoiles ;
- elle a atteint son niveau maximal, soit `10 × K` ;
- l'état observé est stable et confirmé avant le clic d'extraction.

Une poule intermédiaire n'est pas extraite si elle doit encore être améliorée pour un lot supérieur. Une extraction réussie produit un jeton du même niveau d'étoile que la poule.

## 3. Calcul des besoins intermédiaires

On note `B[s]` le nombre de poules à extraire au niveau `s★`.

1. `B[K] = N` pour l'objectif final.
2. Pour chaque niveau `s` de `K-1` à `1` :
   - calculer le nombre de poules destinées à dépasser `s★` : `P[s] = somme(B[j]) pour j > s` ;
   - calculer les jetons `s★` nécessaires : `B[s] = P[s] × coût(s★ → s+1★)`.
3. Le nombre total de poules à capturer est `somme(B[s])`.

### Exemple : 34 jetons 3★

- lot final : `B[3] = 34` poules 3★ à monter niveau 30 puis extraire ;
- passage 2★ → 3★ : `34 × 2 = 68` jetons 2★, donc 68 poules 2★ à monter niveau 20 puis extraire ;
- passage 1★ → 2★ : les 34 poules finales et les 68 poules intermédiaires traversent ce palier, soit `(34 + 68) × 1 = 102` jetons 1★ ;
- total à capturer : `34 + 68 + 102 = 204` poules.

## 4. Résultat attendu du planificateur

Pour chaque objectif, le plan retourne :

- la quantité et l'étoile cibles ;
- les lots à extraire par niveau d'étoile ;
- le niveau maximal de chaque lot ;
- les besoins d'amélioration, dans l'ordre d'exécution ;
- le nombre total de poules à capturer.

## 5. Hors périmètre testable automatiquement dans cette livraison

Le calcul ne prétend pas confirmer : la présence d'une cible, le pourcentage réel de PV, un raté d'attaque, une capture réussie, le transfert vers la réserve XP, l'aggro des protomonstres, le niveau ou les étoiles lus à l'écran, le succès d'une amélioration, le retour au niveau 1 ni le succès d'une extraction. Ces points nécessitent Windows, le client NosTale, les modèles visuels et une calibration réelle.
