from app.core.limits import ConcurrencyGate, SlidingWindowLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_limiter_blocks_after_limit_and_reports_retry_after():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=2, window_s=60, clock=clock)

    assert limiter.check("ip") is None
    clock.now = 10
    assert limiter.check("ip") is None
    clock.now = 20
    assert limiter.check("ip") == 40  # first hit at t=0 leaves the window at t=60


def test_limiter_window_slides():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=1, window_s=60, clock=clock)

    assert limiter.check("ip") is None
    clock.now = 59
    assert limiter.check("ip") is not None
    clock.now = 61
    assert limiter.check("ip") is None


def test_limiter_keys_are_independent():
    limiter = SlidingWindowLimiter(limit=1, window_s=60, clock=FakeClock())
    assert limiter.check("a") is None
    assert limiter.check("b") is None
    assert limiter.check("a") is not None


def test_gate_caps_concurrency_and_frees_slots():
    gate = ConcurrencyGate(max_concurrent=2, clock=FakeClock())
    first, second = gate.try_acquire(), gate.try_acquire()

    assert first is not None and second is not None
    assert gate.try_acquire() is None
    gate.release(first)
    assert gate.try_acquire() is not None


def test_gate_expires_leaked_slots():
    clock = FakeClock()
    gate = ConcurrencyGate(max_concurrent=1, ttl_s=300, clock=clock)

    assert gate.try_acquire() is not None
    assert gate.try_acquire() is None
    clock.now = 301  # the first slot was never released
    assert gate.try_acquire() is not None
