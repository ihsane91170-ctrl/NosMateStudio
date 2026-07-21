import pytest

from app.production import TokenGoal, TokenProductionPlanner


def test_34_three_star_tokens_matches_validated_business_example() -> None:
    plan = TokenProductionPlanner().build(TokenGoal((0, 0, 34, 0, 0)))

    assert plan.tokens_to_extract == (102, 68, 34, 0, 0)
    assert plan.chickens_required == 204
    assert plan.upgrades == (102, 34, 0, 0)


def test_mixed_goal_accumulates_direct_and_intermediate_tokens() -> None:
    plan = TokenProductionPlanner().build(TokenGoal((5, 2, 1, 0, 0)))

    assert plan.tokens_to_extract == (10, 4, 1, 0, 0)
    assert plan.chickens_required == 15


def test_empty_goal_produces_empty_plan() -> None:
    plan = TokenProductionPlanner().build(TokenGoal((0, 0, 0, 0, 0)))
    assert plan.chickens_required == 0


def test_negative_goal_is_rejected() -> None:
    with pytest.raises(ValueError):
        TokenGoal((0, -1, 0, 0, 0))
