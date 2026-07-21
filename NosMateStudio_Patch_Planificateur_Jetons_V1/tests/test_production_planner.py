import pytest

from app.planning.production_planner import (
    PROTOMONSTER_LEVEL_CAPS,
    TokenProductionPlanner,
    chicken_level_cap,
)


def test_plan_for_34_three_star_tokens_calculates_all_intermediate_batches() -> None:
    plan = TokenProductionPlanner().plan(quantity=34, stars=3)

    assert plan.token_quantity(1) == 102
    assert plan.token_quantity(2) == 68
    assert plan.token_quantity(3) == 34
    assert plan.chickens_to_capture == 204


def test_plan_exposes_upgrade_requirements_in_execution_order() -> None:
    plan = TokenProductionPlanner().plan(quantity=34, stars=3)

    assert [(step.from_stars, step.required_tokens) for step in plan.upgrades] == [
        (1, 102),
        (2, 68),
    ]
    assert plan.upgrades[0].chickens_to_upgrade == 102
    assert plan.upgrades[1].chickens_to_upgrade == 34


def test_one_star_tokens_require_only_capture_xp_and_extraction() -> None:
    plan = TokenProductionPlanner().plan(quantity=7, stars=1)

    assert plan.chickens_to_capture == 7
    assert plan.token_quantity(1) == 7
    assert plan.upgrades == ()
    assert plan.batches[0].max_level == 10


def test_zero_quantity_returns_an_empty_plan() -> None:
    plan = TokenProductionPlanner().plan(quantity=0, stars=4)

    assert plan.chickens_to_capture == 0
    assert plan.batches == ()
    assert plan.upgrades == ()


def test_six_star_plan_uses_all_known_upgrade_costs() -> None:
    plan = TokenProductionPlanner().plan(quantity=1, stars=6)

    assert [plan.token_quantity(stars) for stars in range(1, 7)] == [
        240,
        160,
        60,
        15,
        4,
        1,
    ]
    assert plan.chickens_to_capture == 480


@pytest.mark.parametrize("stars", range(1, 7))
def test_chicken_level_cap_is_ten_times_the_star_count(stars: int) -> None:
    assert chicken_level_cap(stars) == stars * 10


def test_protomonster_caps_are_consolidated_in_the_domain_module() -> None:
    assert dict(PROTOMONSTER_LEVEL_CAPS) == {
        "weak": 20,
        "normal": 40,
        "strong": 60,
    }


@pytest.mark.parametrize(
    ("quantity", "stars", "error"),
    [
        (-1, 3, ValueError),
        (1, 0, ValueError),
        (1, 7, ValueError),
        (1.5, 3, TypeError),
        (1, "3", TypeError),
        (True, 3, TypeError),
    ],
)
def test_invalid_objectives_are_rejected(quantity: object, stars: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        TokenProductionPlanner().plan(quantity=quantity, stars=stars)  # type: ignore[arg-type]
