import pytest

from app.inventory import (
    Inventory,
    PetInstance,
    PetProfile,
)
from app.planning import (
    FarmTokensAction,
    StopAction,
    UpgradePetAction,
    UpgradePlanner,
)


def chicken_profile() -> PetProfile:
    return PetProfile(
        id="chicken",
        display_name="Poule",
        disposable=True,
        desired_stars=0,
        template_name="pet_chicken_row",
    )


def ratufu_profile() -> PetProfile:
    return PetProfile(
        id="ratufu",
        display_name="Ratufu",
        disposable=False,
        desired_stars=6,
        template_name="pet_ratufu_row",
    )


def inventory_with_ratufu(
    *,
    stars: int,
) -> Inventory:
    inventory = Inventory()

    inventory.add(
        PetInstance(
            profile=ratufu_profile(),
            stars=stars,
        )
    )

    return inventory


@pytest.mark.parametrize(
    ("stars", "expected_cost"),
    [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 3),
        (5, 4),
    ],
)
def test_planner_upgrades_when_tokens_are_sufficient(
    stars: int,
    expected_cost: int,
) -> None:
    action = UpgradePlanner().plan(
        inventory_with_ratufu(stars=stars),
        tokens=expected_cost,
        goal_profile_id="ratufu",
    )

    assert isinstance(action, UpgradePetAction)
    assert action.profile_id == "ratufu"
    assert action.current_stars == stars
    assert action.target_stars == stars + 1
    assert action.cost == expected_cost


def test_planner_farms_tokens_when_tokens_are_missing() -> None:
    action = UpgradePlanner().plan(
        inventory_with_ratufu(stars=4),
        tokens=1,
        goal_profile_id="ratufu",
    )

    assert isinstance(action, FarmTokensAction)
    assert action.required_tokens == 3
    assert action.missing_tokens == 2


def test_planner_stops_when_goal_is_reached() -> None:
    action = UpgradePlanner().plan(
        inventory_with_ratufu(stars=6),
        tokens=300,
        goal_profile_id="ratufu",
    )

    assert isinstance(action, StopAction)
    assert "objectif est atteint" in action.reason.lower()


def test_planner_stops_when_goal_pet_is_missing() -> None:
    inventory = Inventory()

    inventory.add(
        PetInstance(
            profile=chicken_profile(),
            stars=1,
        )
    )

    action = UpgradePlanner().plan(
        inventory,
        tokens=10,
        goal_profile_id="ratufu",
    )

    assert isinstance(action, StopAction)
    assert "aucun familier" in action.reason.lower()


def test_planner_uses_most_advanced_goal_pet() -> None:
    inventory = Inventory()
    profile = ratufu_profile()

    inventory.add(
        PetInstance(
            profile=profile,
            stars=2,
        )
    )
    inventory.add(
        PetInstance(
            profile=profile,
            stars=4,
        )
    )

    action = UpgradePlanner().plan(
        inventory,
        tokens=3,
        goal_profile_id="ratufu",
    )

    assert isinstance(action, UpgradePetAction)
    assert action.current_stars == 4
    assert action.target_stars == 5


def test_planner_rejects_negative_token_count() -> None:
    with pytest.raises(ValueError):
        UpgradePlanner().plan(
            inventory_with_ratufu(stars=4),
            tokens=-1,
            goal_profile_id="ratufu",
        )