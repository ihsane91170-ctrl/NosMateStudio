import pytest

from app.planning.production_planner import ProductionPlanner


def test_one_token_one_star_requires_one_chicken() -> None:
    plan = ProductionPlanner().plan(1, 1)
    assert plan.quantity_for(1) == 1
    assert plan.chickens_to_capture == 1


def test_reference_case_34_tokens_three_stars() -> None:
    plan = ProductionPlanner().plan(34, 3)
    assert plan.quantity_for(1) == 102
    assert plan.quantity_for(2) == 68
    assert plan.quantity_for(3) == 34
    assert plan.chickens_to_capture == 204


def test_intermediate_producers_are_included_recursively() -> None:
    plan = ProductionPlanner().plan(1, 4)
    assert [batch.quantity for batch in plan.batches] == [12, 8, 3, 1]
    assert plan.chickens_to_capture == 24


@pytest.mark.parametrize("stars", range(1, 7))
def test_extraction_level_is_ten_times_stars(stars: int) -> None:
    plan = ProductionPlanner().plan(1, stars)
    assert plan.batches[-1].extraction_level == stars * 10


@pytest.mark.parametrize("quantity", [1, 2, 17, 34])
def test_target_batch_matches_requested_quantity(quantity: int) -> None:
    plan = ProductionPlanner().plan(quantity, 3)
    assert plan.quantity_for(3) == quantity


@pytest.mark.parametrize("quantity", [0, -1, -100])
def test_quantity_must_be_positive(quantity: int) -> None:
    with pytest.raises(ValueError, match="strictement positive"):
        ProductionPlanner().plan(quantity, 1)


@pytest.mark.parametrize("stars", [0, 7, 99])
def test_stars_must_be_between_one_and_six(stars: int) -> None:
    with pytest.raises(ValueError, match="compris entre 1 et 6"):
        ProductionPlanner().plan(1, stars)
