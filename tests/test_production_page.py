from app.ui.pages.production_page import ProductionPage


def test_page_calculates_and_renders_plan(qtbot) -> None:
    page = ProductionPage()
    qtbot.addWidget(page)

    page.findChild(type(page.capture_count), "tokenGoal3").setValue(34)
    qtbot.mouseClick(page.calculate_button, __import__("PySide6").QtCore.Qt.LeftButton)

    assert page.last_plan is not None
    assert page.last_plan.chickens_required == 204
    assert "204 poule" in page.summary.text()
    assert page.plan_table.item(0, 2).text() == "102"
    assert page.plan_table.item(1, 2).text() == "68"
    assert page.plan_table.item(2, 2).text() == "34"


def test_capture_preparation_emits_requested_count(qtbot) -> None:
    page = ProductionPage()
    qtbot.addWidget(page)
    page.capture_count.setValue(12)

    with qtbot.waitSignal(page.capture_requested) as blocker:
        qtbot.mouseClick(page.capture_button, __import__("PySide6").QtCore.Qt.LeftButton)

    assert blocker.args == [12]
