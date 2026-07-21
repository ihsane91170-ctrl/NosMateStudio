from app.capture import CaptureBatchConfig, CaptureBatchController, CaptureBatchStatus


class CaptureStub:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0

    def capture_one(self):
        self.calls += 1
        return next(self.outcomes)


class ReturnStub:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0

    def return_to_exp_zone(self):
        self.calls += 1
        return next(self.outcomes)


def test_capture_n_chickens_then_return_once_after_full_batch():
    capture = CaptureStub([True, True, True])
    returns = ReturnStub([True])

    result = CaptureBatchController(capture, returns).run(CaptureBatchConfig(3))

    assert result.completed
    assert result.captured_count == 3
    assert capture.calls == 3
    assert returns.calls == 1


def test_retry_current_chicken_before_counting_it():
    capture = CaptureStub([False, False, True])
    returns = ReturnStub([True])

    result = CaptureBatchController(capture, returns).run(
        CaptureBatchConfig(1, max_capture_attempts_per_chicken=3)
    )

    assert result.completed
    assert result.total_capture_attempts == 3
    assert returns.calls == 1


def test_stop_when_capture_limit_is_reached():
    capture = CaptureStub([False, False])
    returns = ReturnStub([])

    result = CaptureBatchController(capture, returns).run(
        CaptureBatchConfig(1, max_capture_attempts_per_chicken=2)
    )

    assert result.status is CaptureBatchStatus.CAPTURE_FAILED
    assert result.captured_count == 0
    assert returns.calls == 0


def test_all_captures_are_kept_when_final_return_fails():
    capture = CaptureStub([True, True])
    returns = ReturnStub([False])

    result = CaptureBatchController(capture, returns).run(CaptureBatchConfig(2))

    assert result.status is CaptureBatchStatus.RETURN_FAILED
    assert result.captured_count == 2
    assert capture.calls == 2
    assert returns.calls == 1


class CaptureWithStandbyStub(CaptureStub):
    def __init__(self, outcomes, standby_outcome=True):
        super().__init__(outcomes)
        self.standby_calls = 0
        self.standby_outcome = standby_outcome
        self.last_message = ""

    def put_first_companion_on_standby(self):
        self.standby_calls += 1
        if not self.standby_outcome:
            self.last_message = "S n'a pas pu être envoyé."
        return self.standby_outcome


def test_first_captured_chicken_is_put_on_standby_once_only():
    capture = CaptureWithStandbyStub([True, True, True])
    returns = ReturnStub([True])

    result = CaptureBatchController(capture, returns).run(CaptureBatchConfig(3))

    assert result.completed
    assert capture.standby_calls == 1
    assert capture.calls == 3


def test_capture_retries_do_not_trigger_standby_before_success():
    capture = CaptureWithStandbyStub([False, False, True, True])
    returns = ReturnStub([True])

    result = CaptureBatchController(capture, returns).run(
        CaptureBatchConfig(2, max_capture_attempts_per_chicken=3)
    )

    assert result.completed
    assert capture.standby_calls == 1
    assert capture.calls == 4


def test_batch_stops_when_first_companion_cannot_be_put_on_standby():
    capture = CaptureWithStandbyStub([True, True], standby_outcome=False)
    returns = ReturnStub([])

    result = CaptureBatchController(capture, returns).run(CaptureBatchConfig(2))

    assert result.status is CaptureBatchStatus.STANDBY_FAILED
    assert result.captured_count == 1
    assert capture.calls == 1
    assert capture.standby_calls == 1
    assert returns.calls == 0


class ClassifiedCaptureStub:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0
        self.last_attempt_kind = None
        self.last_message = ""

    def capture_one(self):
        success, kind, message = next(self.outcomes)
        self.calls += 1
        self.last_attempt_kind = kind
        self.last_message = message
        return success


def test_rejected_targets_do_not_consume_capture_quota():
    from app.capture import CaptureAttemptKind

    capture = ClassifiedCaptureStub([
        (False, CaptureAttemptKind.SEARCH_REJECTED, "mauvaise cible 1"),
        (False, CaptureAttemptKind.SEARCH_REJECTED, "mauvaise cible 2"),
        (False, CaptureAttemptKind.SEARCH_REJECTED, "mauvaise cible 3"),
        (False, CaptureAttemptKind.SEARCH_REJECTED, "mauvaise cible 4"),
        (True, CaptureAttemptKind.CAPTURED, "poule capturée"),
    ])
    returns = ReturnStub([True])

    result = CaptureBatchController(capture, returns).run(
        CaptureBatchConfig(
            1,
            max_capture_attempts_per_chicken=1,
            max_search_attempts_per_chicken=10,
        )
    )

    assert result.completed
    assert result.total_search_attempts == 5
    assert result.total_capture_attempts == 1
    assert capture.calls == 5


def test_search_limit_is_independent_from_capture_limit():
    from app.capture import CaptureAttemptKind

    capture = ClassifiedCaptureStub([
        (False, CaptureAttemptKind.SEARCH_REJECTED, "rejet 1"),
        (False, CaptureAttemptKind.SEARCH_REJECTED, "rejet 2"),
        (False, CaptureAttemptKind.SEARCH_REJECTED, "rejet 3"),
    ])
    returns = ReturnStub([])

    result = CaptureBatchController(capture, returns).run(
        CaptureBatchConfig(
            1,
            max_capture_attempts_per_chicken=10,
            max_search_attempts_per_chicken=3,
        )
    )

    assert result.status is CaptureBatchStatus.SEARCH_EXHAUSTED
    assert result.total_search_attempts == 3
    assert result.total_capture_attempts == 0
    assert returns.calls == 0


def test_real_capture_failures_still_consume_capture_quota():
    from app.capture import CaptureAttemptKind

    capture = ClassifiedCaptureStub([
        (False, CaptureAttemptKind.CAPTURE_FAILED, "capture ratée 1"),
        (False, CaptureAttemptKind.CAPTURE_FAILED, "capture ratée 2"),
    ])
    returns = ReturnStub([])

    result = CaptureBatchController(capture, returns).run(
        CaptureBatchConfig(
            1,
            max_capture_attempts_per_chicken=2,
            max_search_attempts_per_chicken=20,
        )
    )

    assert result.status is CaptureBatchStatus.CAPTURE_FAILED
    assert result.total_capture_attempts == 2
    assert result.total_search_attempts == 2
