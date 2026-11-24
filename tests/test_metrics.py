import pytest
from cpstudy.metrics import opportunity_freshness, freshness_fraction


def test_newer_observation_can_cover_suppressed_demand():
    opportunities=[dict(opportunity_id="old",acquisition_ns=0,deadline_ns=100,
                        source_id=0,receiver_ids=[1],evaluated=True,generated=False)]
    terminal={("new",1):dict(reason="success",at_ns=80,acquisition_ns=50,source_id=0)}
    assert opportunity_freshness(opportunities,terminal)==(1,1)
    terminal[("new",1)]["at_ns"]=101
    assert opportunity_freshness(opportunities,terminal)==(0,1)


def test_deadline_boundary_is_inclusive():
    opportunity=dict(opportunity_id="demand",acquisition_ns=0,deadline_ns=100,
                     source_id=0,receiver_ids=[1],evaluated=True,generated=True)
    terminal={("at-deadline",1):dict(reason="success",at_ns=100,
                                      acquisition_ns=0,source_id=0)}
    assert opportunity_freshness([opportunity],terminal)==(1,1)
    terminal[("at-deadline",1)]["at_ns"]=101
    assert opportunity_freshness([opportunity],terminal)==(0,1)


def test_one_update_can_cover_multiple_older_opportunities():
    opportunities=[
        dict(opportunity_id="old",acquisition_ns=0,deadline_ns=100,
             source_id=0,receiver_ids=[1],evaluated=True,generated=False),
        dict(opportunity_id="newer",acquisition_ns=50,deadline_ns=150,
             source_id=0,receiver_ids=[1],evaluated=True,generated=True),
    ]
    terminal={("newer-message",1):dict(reason="success",at_ns=80,
                                        acquisition_ns=50,source_id=0)}
    assert opportunity_freshness(opportunities,terminal)==(2,2)


def test_time_coverage_accounts_for_initial_outage_and_stale_updates():
    # Fresh over [10,50] and [80,120] in a [0,150] window.
    assert freshness_fraction([(10,0),(80,70)],0,150,50)==pytest.approx(80/150)
    assert freshness_fraction([],0,100,50)==0
    # An out-of-order observation at t=90 cannot erase the acquisition at 70.
    assert freshness_fraction([(10,0),(80,70),(90,5)],0,150,50)==pytest.approx(80/150)
    assert freshness_fraction([(10,0)],20,100,50)==pytest.approx(30/80)
