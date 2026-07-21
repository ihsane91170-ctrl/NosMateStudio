from app.planning.production_planner import TokenProductionPlanner
from app.production import ProductionOrchestrator, ProductionStage


def test_simulation_completes_one_token_one_star() -> None:
    events = []
    plan = TokenProductionPlanner().plan(quantity=1, stars=1)
    result = ProductionOrchestrator(events.append).run_simulation(plan)

    assert result.succeeded
    assert result.produced_tokens == 1
    assert result.requested_tokens == 1
    assert events[-1].stage is ProductionStage.COMPLETED
    assert events[-1].progress_percent == 100
    assert any(event.stage is ProductionStage.CAPTURE for event in events)
    assert any(event.stage is ProductionStage.RESERVE_XP for event in events)
    assert any(event.stage is ProductionStage.LEVELING for event in events)
    assert any(event.stage is ProductionStage.EXTRACTION for event in events)


def test_simulation_follows_intermediate_batches_and_upgrades() -> None:
    events = []
    plan = TokenProductionPlanner().plan(quantity=1, stars=3)
    result = ProductionOrchestrator(events.append).run_simulation(plan)

    assert result.succeeded
    messages = "\n".join(event.message for event in events)
    assert "6 poules" in messages
    assert "3 jetons 1★" in messages
    assert "2 jetons 2★" in messages
    assert "retour niveau 1 attendu" in messages


def test_stop_request_interrupts_at_next_boundary() -> None:
    events = []
    orchestrator = None

    def on_event(event) -> None:
        events.append(event)
        if event.stage is ProductionStage.CAPTURE:
            orchestrator.request_stop()

    orchestrator = ProductionOrchestrator(on_event)
    plan = TokenProductionPlanner().plan(quantity=34, stars=3)
    result = orchestrator.run_simulation(plan)

    assert result.stage is ProductionStage.STOPPED
    assert not result.succeeded
    assert events[-1].stage is ProductionStage.STOPPED


def test_zero_quantity_is_a_successful_noop() -> None:
    plan = TokenProductionPlanner().plan(quantity=0, stars=2)
    result = ProductionOrchestrator().run_simulation(plan)

    assert result.succeeded
    assert result.produced_tokens == 0
