# Contribution

## Workflow Git

Créer une branche depuis `develop` :

```bash
git checkout develop
git pull
git checkout -b feature/US001-detection-nostale
```

Après développement :

```bash
git add .
git commit -m "feat(US001): detect NosTale window"
git push -u origin feature/US001-detection-nostale
```

Créer ensuite une Pull Request vers `develop`.

À la fin du sprint, créer une Pull Request de `develop` vers `main`.

## Convention de commits

Le projet utilise une convention inspirée de Conventional Commits :

- `feat(US001): ...`
- `fix(US003): ...`
- `test(US007): ...`
- `docs: ...`
- `refactor: ...`
- `chore: ...`

## Definition of Done

Une User Story est terminée lorsque :

- les critères d'acceptation sont couverts ;
- les tests associés passent ;
- aucun secret ni fichier local n'est versionné ;
- la documentation utile est mise à jour ;
- la Pull Request est relue et validée ;
- le Product Owner a validé le comportement.
