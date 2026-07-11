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
    assert "Clavier : ['Q', '_']" in logs