import csv
import gzip
import pytest
from cpstudy.config import validate
from cpstudy.network_audit import audit_network


def fixture(tmp_path,unverified=False):
    events=[dict(event_ns=0,trace_order=0,source_id=1,receiver_id=0,sequence=0,kind=1,
                 acquisition_ns=0,event_type='reception',reason='',reported_backlog=0,queue_depth=0),
            dict(event_ns=10,trace_order=2,source_id=1,receiver_id=0,sequence=0,kind=1,
                 acquisition_ns=0,event_type='verification_end',reason='',reported_backlog=0,queue_depth=1),
            dict(event_ns=10,trace_order=3,source_id=1,receiver_id=0,sequence=0,kind=1,
                 acquisition_ns=0,event_type='terminal',reason='feedback_ready',reported_backlog=0,queue_depth=1)]
    controls=[dict(event_ns=1,trace_order=1,node_id=0,rate_hz=8,busy_fraction=0,
                   remote_backlog=0,feedback_stale=0 if unverified else 1,
                   observed_neighbors=1 if unverified else 0),
              dict(event_ns=20,trace_order=4,node_id=0,rate_hz=8,busy_fraction=0,
                   remote_backlog=0,feedback_stale=0,observed_neighbors=1),
              dict(event_ns=30,trace_order=5,node_id=0,rate_hz=8.5,busy_fraction=0,
                   remote_backlog=0,feedback_stale=0,observed_neighbors=1)]
    for name,rows in [('network-events',events),('network-controls',controls)]:
        with gzip.open(tmp_path/(name+'.csv.gz'),'wt') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def test_feedback_is_available_only_after_authentication(tmp_path):
    fixture(tmp_path)
    result=audit_network(tmp_path,validate({'policy':'joint','sources':2}))
    assert result['control_decisions_checked']==3


def test_oracle_feedback_is_rejected(tmp_path):
    fixture(tmp_path,unverified=True)
    with pytest.raises(ValueError,match='unavailable receiver feedback'):
        audit_network(tmp_path,validate({'policy':'joint','sources':2}))
