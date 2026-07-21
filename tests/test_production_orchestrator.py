import pytest

from app.production import ProductionOrchestrator, ProductionState


def test_pilot_cycle_one_token_one_star_finishes() -> None:
    result = ProductionOrchestrator().run(1, 1)
    assert result.succeeded
    assert result.produced_quantity == 1
    assert result.requested_quantity == 1
    assert result.events[-1].state is ProductionState.FINISHED
    assert result.events[-1].progress_percent == 100


def test_cycle_emits_expected_states() -> None:
    result = ProductionOrchestrator().run(1, 1)
    states = [event.state for event in result.events]
    assert states == [
        ProductionState.PLANNING,
        ProductionState.PREFLIGHT,
        ProductionState.CAPTURING,
        ProductionState.RESERVING,
        ProductionState.LEVELING,
        ProductionState.EXTRACTING,
        ProductionState.FINISHED,
    ]


def test_three_star_cycle_contains_upgrade_steps() -> None:
    result = ProductionOrchestrator().run(1, 3)
    assert ProductionState.UPGRADING in [event.state for event in result.events]


def test_listener_receives_every_event() -> None:
    received = []
    result = ProductionOrchestrator().run(1, 1, listener=received.append)
    assert received == list(result.events)


def test_stop_request_from_listener_stops_before_next_step() -> None:
    orchestrator = ProductionOrchestrator()

    def stop_after_plan(event) -> None:
        if event.state is ProductionState.PLANNING:
            orchestrator.request_stop()

    result = orchestrator.run(1, 1, listener=stop_after_plan)
    assert result.state is ProductionState.STOPPED
    assert not result.succeeded
    assert result.events[-1].state is ProductionState.STOPPED


def test_new_run_resets_previous_stop_request() -> None:
    orchestrator = ProductionOrchestrator()
    orchestrator.request_stop()
    result = orchestrator.run(1, 1)
    assert result.succeeded


def test_real_mode_is_explicitly_locked() -> None:
    with pytest.raises(RuntimeError, match="mode réel est verrouillé"):
        ProductionOrchestrator().run(1, 1, simulation=False)


def test_reference_case_finishes_with_requested_final_tokens() -> None:
    result = ProductionOrchestrator().run(34, 3)
    assert result.succeeded
    assert result.produced_quantity == 34
    assert "34/34" in result.events[-1].message
