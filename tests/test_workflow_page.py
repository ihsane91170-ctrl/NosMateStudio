from app.ui.pages.workflow_page import WorkflowPage


def test_workflow_page_runs_demo_simulation(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    page.run_button.click()

    assert page.state_label.text() == "État : terminé"

    logs = page.log_output.toPlainText()

    assert "workflow_started" in logs
    assert "workflow_finished" in logs
    assert "Résumé de la simulation" in logs
    assert "Clavier :" in logs

def test_real_countdown_updates_logs(
    qtbot,
    monkeypatch,
) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    monkeypatch.setattr(
        "app.ui.pages.workflow_page.time.sleep",
        lambda _seconds: None,
    )

    page._run_countdown(seconds=3)

    logs = page.log_output.toPlainText()

    assert "Démarrage réel dans 3..." in logs
    assert "Démarrage réel dans 2..." in logs
    assert "Démarrage réel dans 1..." in logs
    assert "GO" in logs
    assert page.state_label.text() == "État : exécution réelle"