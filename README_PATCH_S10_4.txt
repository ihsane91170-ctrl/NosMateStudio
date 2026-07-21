NosMate Studio — Patch S10.4

Règle ajoutée :
- après la première capture confirmée du lot, NosMate active NosTale ;
- envoie S une seule fois pour mettre la poule accompagnatrice en mode Rester ;
- attend brièvement ;
- poursuit les captures 2 à N sans renvoyer S ;
- retourne en zone d'XP une seule fois après la fin du lot, puis confirme avec Entrée.

Le contrôleur s'arrête avec STANDBY_FAILED si S ne peut pas être envoyé, afin de ne pas continuer avec une poule susceptible d'attaquer les prochaines cibles.
