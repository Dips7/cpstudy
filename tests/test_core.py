import math
import heapq
import pytest
from cpstudy.model import mg1, offered_load_bps, muhammad2019_mean
from cpstudy.config import validate, digest
from cpstudy.policy import Controller
from cpstudy.receiver import Receiver, Update


def test_units_and_broadcast():
    assert offered_load_bps(20, 10, 1100) == 1_760_000
    # No receiver multiplier belongs in a broadcast offered-load calculation.
    assert offered_load_bps(1, 1, 1000) == 8000


def test_queue_known_mm1_limit():
    # Exponential service => mean sojourn = 1 / (mu - lambda).
    p = mg1(40, .01, 2 * .01**2)
    assert p.mean_sojourn_s == pytest.approx(1 / (100 - 40))
    assert mg1(100, .01, .0001).mean_wait_s is None
    assert mg1(0, .01, .0001).mean_wait_s == 0
    with pytest.raises(ValueError):
        mg1(10, .01, .00001)


def test_controller_hysteresis_bounds_and_staleness():
    c = validate({"policy":"joint"})
    p = Controller(10)
    assert p.update(c, 0, 0, stale=True) == 8
    assert p.update(c, 0, 0) == 8
    assert p.update(c, 0, 0) == 8.5
    for _ in range(100): p.update(c, 1, 100)
    assert p.rate == 1
    for _ in range(100): p.update(c, 0, 0)
    assert p.rate == 10


def test_config_validation():
    for changes in ({"sources":1}, {"max_rate_hz":20}, {"verify_ms":-1},
                    {"duration_s":math.nan}, {"policy":"oracle"}, {"typo":1},
                    {"verify_ms":"fast"},{"sources":True},{"radio":[]},{1:1}):
        with pytest.raises(ValueError): validate(changes)
    a = validate({})
    assert digest(a) == digest(a | {"output":"elsewhere"})


def receiver_fixture(capacity=1, verify=10, fusion=2):
    events, logs, terminals = [], [], []
    def schedule(t, fn, u): heapq.heappush(events, (t, len(logs), fn, u))
    r = Receiver(1, capacity, verify, fusion, schedule,
                 lambda *args: logs.append(args), lambda *args: terminals.append(args))
    def drain():
        while events:
            t, _, fn, u = heapq.heappop(events); fn(t,u)
    return r, drain, logs, terminals


def update(i, acquired=0, deadline=100):
    return Update(0,1,str(i),str(i),acquired,deadline,1100,1200)


def test_single_update_exact_timing_and_authentication_order():
    r, drain, logs, terminal = receiver_fixture()
    r.receive(3, update(0))
    assert r.latest == {}
    drain()
    assert [(x[0],x[1]) for x in logs] == [
        (3,"reception"),(3,"verification_start"),(13,"verification_end"),(15,"fusion_ready")]
    assert terminal[0][0] == 15 and terminal[0][2] == "success"


def test_finite_queue_overflow_and_expiry():
    r, drain, logs, terminal = receiver_fixture()
    for i in range(3): r.receive(0,update(i,deadline=15))
    drain()
    assert sorted(x[2] for x in terminal) == ["queue_overflow","success","verification_expired"]
    assert len({x[1].message for x in terminal}) == 3


def test_out_of_order_never_regresses_age():
    r, drain, _, terminal = receiver_fixture()
    r.receive(10,update(1,acquired=10)); drain()
    r.receive(30,update(2,acquired=5)); drain()
    assert r.latest[0] == 10


def test_published_three_stage_equation():
    # Direct equation (2): sender lambda=10, shared-stage load N*lambda=100.
    expected=1/(1000-10)+1/(10000-100)+1/(2000-100)+.009
    assert muhammad2019_mean(10,10,.001,.0001,.0005,.009)==pytest.approx(expected)
    assert muhammad2019_mean(10,200,.001,.0001,.0005) is None
