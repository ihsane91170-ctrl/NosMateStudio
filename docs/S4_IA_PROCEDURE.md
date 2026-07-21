# S4 IA — procédure

1. Constituer `vision_dataset` avec `python tools/annotate_chickens.py`.
2. Annoter chaque poule comme `chicken` et chaque autre monstre comme `not_chicken`.
3. Installer l'entraînement : `python -m pip install ultralytics`.
4. Lancer : `python tools/train_chicken_detector.py --epochs 50`.
5. Copier `training_runs/chicken_detector/weights/best.pt` vers `assets/models/chicken_detector.pt`.
6. Le détecteur peut ensuite être appelé par `UltralyticsObjectDetector`.

Aucun modèle fiable n'est inclus : les deux petits templates fournis ne constituent pas un dataset suffisant.
