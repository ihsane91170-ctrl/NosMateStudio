# ADR-006 — Introduire un Workflow Engine générique

## Statut

Accepté.

## Contexte

Les futures automatisations doivent enchaîner des étapes, gérer les erreurs et exposer leur état
sans coupler la logique à l'interface graphique ou à NosTale.

## Décision

Créer un moteur synchrone et générique basé sur :

- `WorkflowState`
- `WorkflowContext`
- `WorkflowStep`
- `StepResult`
- `WorkflowEngine`

## Conséquences

### Positives

- Les futurs workflows seront des assemblages d'étapes.
- Le moteur est testable sans interface graphique.
- La gestion des erreurs est centralisée.
- Les événements peuvent être adaptés ensuite aux signaux Qt.

### Limites initiales

- Le moteur est synchrone.
- Le retry n'est pas encore implémenté.
- La pause reprend dans une future PR.
