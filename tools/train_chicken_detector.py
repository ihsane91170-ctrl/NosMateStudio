from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Entraîne le détecteur IA NosMate.")
    parser.add_argument("--data", type=Path, default=Path("vision_dataset/dataset.yaml"))
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--base-model", default="yolov8n.pt")
    args = parser.parse_args()

    if not args.data.is_file():
        parser.error(f"Dataset introuvable : {args.data}")

    try:
        from ultralytics import YOLO
    except ImportError:
        parser.error("ultralytics absent. Installez-le avec : python -m pip install ultralytics")

    model = YOLO(args.base_model)
    result = model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        project="training_runs",
        name="chicken_detector",
    )
    print("Entraînement terminé.")
    print("Copiez best.pt depuis training_runs/chicken_detector/weights/ vers assets/models/chicken_detector.pt")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
