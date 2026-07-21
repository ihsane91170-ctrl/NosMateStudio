from app.ui.pages.production_planner_page import ProductionPlannerPage


def test_page_displays_default_34_tokens_3_stars_plan(qtbot) -> None:
    page = ProductionPlannerPage()
    qtbot.addWidget(page)

    assert page.current_plan is not None
    assert page.current_plan.target_quantity == 34
    assert page.current_plan.target_stars == 3
    assert page.current_plan.chickens_to_capture == 204
    assert page.batch_table.rowCount() == 3
    assert page.batch_table.item(0, 1).text() == "102"
    assert page.batch_table.item(1, 1).text() == "68"
    assert page.batch_table.item(2, 1).text() == "34"
    assert "204 poules" in page.summary_label.text()


def test_page_recalculates_after_user_changes_objective(qtbot) -> None:
    page = ProductionPlannerPage()
    qtbot.addWidget(page)

    page.quantity_input.setValue(10)
    page.stars_input.setCurrentIndex(1)  # 2★
    page.calculate_button.click()

    assert page.current_plan is not None
    assert page.current_plan.target_quantity == 10
    assert page.current_plan.target_stars == 2
    assert page.current_plan.token_quantity(1) == 10
    assert page.current_plan.token_quantity(2) == 10
    assert page.current_plan.chickens_to_capture == 20
    assert page.batch_table.rowCount() == 2
    assert "20 poules" in page.summary_label.text()
