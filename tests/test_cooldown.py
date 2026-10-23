from services.cooldown import Cooldown


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def test_allowed_before_first_use():
    assert Cooldown(30, clock=FakeClock()).remaining() == 0


def test_blocked_right_after_start():
    clock = FakeClock()
    cd = Cooldown(30, clock=clock)
    cd.start()
    assert cd.remaining() == 30


def test_counts_down_and_rounds_up():
    clock = FakeClock()
    cd = Cooldown(30, clock=clock)
    cd.start()
    clock.now += 10.2
    assert cd.remaining() == 20  # 19.8 seconds left, shown as 20


def test_allowed_again_after_time_passes():
    clock = FakeClock()
    cd = Cooldown(30, clock=clock)
    cd.start()
    clock.now += 30
    assert cd.remaining() == 0


def test_can_restart_after_expiry():
    clock = FakeClock()
    cd = Cooldown(30, clock=clock)
    cd.start()
    clock.now += 31
    cd.start()
    assert cd.remaining() == 30
