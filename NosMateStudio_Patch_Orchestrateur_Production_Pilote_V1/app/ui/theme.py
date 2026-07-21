def build_stylesheet() -> str:
    return """
    QWidget {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: "Segoe UI";
        font-size: 13px;
    }

    QFrame#Sidebar {
        background-color: #111827;
        border-right: 1px solid #334155;
    }

    QLabel#AppTitle {
        font-size: 20px;
        font-weight: 700;
    }

    QLabel#PageTitle {
        font-size: 24px;
        font-weight: 700;
    }

    QLabel#Muted {
        color: #94A3B8;
    }

    QPushButton {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 10px;
        text-align: left;
    }

    QPushButton:hover {
        background-color: #1F2937;
    }

    QPushButton:checked {
        background-color: #2563EB;
        color: white;
    }

    QFrame#Card {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QPushButton#PrimaryButton {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        text-align: center;
    }

    QPushButton#PrimaryButton:hover {
        background-color: #1D4ED8;
    }

    QSpinBox, QComboBox, QTableWidget {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 6px;
    }

    QHeaderView::section {
        background-color: #1E293B;
        color: #F8FAFC;
        border: none;
        padding: 7px;
    }

    QStatusBar {
        background-color: #111827;
        color: #94A3B8;
    }
    """