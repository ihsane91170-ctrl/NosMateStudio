import tkinter as tk
from tkinter import ttk

from app import __version__


def run_app() -> None:
    root = tk.Tk()
    root.title(f"NosMate Studio — {__version__}")
    root.geometry("760x480")
    root.minsize(700, 430)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    container = ttk.Frame(root, padding=18)
    container.pack(fill="both", expand=True)

    ttk.Label(
        container,
        text="NosMate Studio",
        font=("Segoe UI", 20, "bold"),
    ).pack(anchor="w")

    ttk.Label(
        container,
        text="Sprint 0 — Fondations du produit",
        font=("Segoe UI", 11),
    ).pack(anchor="w", pady=(0, 18))

    diagnostic = ttk.LabelFrame(container, text="Diagnostic", padding=14)
    diagnostic.pack(fill="x")

    rows = [
        ("Client NosTale", "Non testé — US001"),
        ("Configuration", "Structure prête — US002"),
        ("Calibration", "À développer — US003"),
        ("Mode simulation", "Prévu"),
    ]

    for row, (label, value) in enumerate(rows):
        ttk.Label(diagnostic, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Label(diagnostic, text=value).grid(row=row, column=1, sticky="w", padx=(25, 0))
    diagnostic.columnconfigure(1, weight=1)

    workflow = ttk.LabelFrame(container, text="Workflow Sprint 1", padding=14)
    workflow.pack(fill="x", pady=14)

    ttk.Label(
        workflow,
        text=(
            "Capture → Téléportation → Invocation → "
            "Affectation F1/F2/F3 → Session prête"
        ),
    ).pack(anchor="w")

    status = ttk.LabelFrame(container, text="État", padding=14)
    status.pack(fill="both", expand=True)

    ttk.Label(
        status,
        text="Le socle du projet est prêt. La prochaine branche sera "
             "feature/US001-detection-nostale.",
        wraplength=650,
        justify="left",
    ).pack(anchor="w")

    ttk.Button(container, text="Fermer", command=root.destroy).pack(anchor="e", pady=(14, 0))

    root.mainloop()
