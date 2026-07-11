from app.executors.keyboard import (
    PyAutoGUIKeyboardExecutor,
    SimulationKeyboardExecutor,
)
from app.ui.pages.workflow_page import WorkflowPage


def test_workflow_page_defaults_to_simulation(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    assert page.simulation_radio.isChecked() is True
    assert page.real_radio.isChecked() is False
    assert page.cycles_input.value() == 1
    assert page.stop_button.isEnabled() is False


def test_workflow_page_lists_registered_workflows(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    names = [
        page.workflow_selector.itemText(index)
        for index in range(page.workflow_selector.count())
    ]

    assert names == [
        "Demo Workflow",
        "Pet XP Workflow",
    ]


def test_workflow_page_runs_multiple_simulation_cycles(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    page.workflow_selector.setCurrentText("Pet XP Workflow")
    page.cycles_input.setValue(2)
    page.run_button.click()

    assert page.state_label.text() == "État : terminé"
    assert page.cycle_label.text() == "Cycle : 2 / 2"
    assert page.progress_bar.value() == 100

    logs = page.log_output.toPlainText()

    assert "Cycles demandés : 2" in logs
    assert "--- Cycle 1 / 2 ---" in logs
    assert "--- Cycle 2 / 2 ---" in logs
    assert "Clavier : ['Q', 'W', '_', '1', '2', '3'," in logs


def test_real_mode_is_not_enabled_yet(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    page.real_radio.setChecked(True)
    page.run_button.click()

    assert (
        page.state_label.text()
        == "État : le mode réel n'est pas encore activé"
    )
    assert "prochaine étape" in page.log_output.toPlainText()

def test_page_creates_simulation_runtime_by_default(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    runtime = page._create_runtime()

    assert isinstance(runtime.keyboard, SimulationKeyboardExecutor)


def test_page_can_build_real_runtime(qtbot) -> None:
    page = WorkflowPage()
    qtbot.addWidget(page)

    page.real_radio.setChecked(True)

    runtime = page._create_runtime()

    assert isinstance(runtime.keyboard, PyAutoGUIKeyboardExecutor)
    assert runtime.keyboard.enabled is True