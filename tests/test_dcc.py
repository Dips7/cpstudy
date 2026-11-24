import pytest
from cpstudy.dcc import AdaptiveDcc,airtime_s


def test_published_adaptive_core_and_physical_units():
    assert airtime_s(1200)==pytest.approx(.001736)
    d=AdaptiveDcc()
    rate=d.update(1,1,1200,10)
    assert d.estimate==.5
    assert d.delta==pytest.approx(.005*.984+.0012*(.68-.5))
    assert rate==pytest.approx(d.delta/.001736)
    for _ in range(1000):d.update(1,1,1200,10)
    assert d.delta==.0006
    assert d.update(1,1,1200,10)==1
    for _ in range(1000):d.update(0,0,1200,10)
    assert d.delta==.03
    assert d.update(0,0,1200,10)==10
