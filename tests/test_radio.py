from cpstudy.config import validate
from cpstudy.radio import NetworkReplay


def test_actual_receives_and_missing_receptions_are_distinguished():
    c=validate({"radio":"ns3","scenario":"static-pilot","sources":2,
                "duration_s":1,"warmup_s":0})
    e=NetworkReplay(c,1)
    e.radio_rows=[
        dict(event_ns='11000000',event_type='send',source_id='0',receiver_id='-1',sequence='0',payload_bytes='1200'),
        dict(event_ns='12000000',event_type='rx',source_id='0',receiver_id='1',sequence='0',payload_bytes='1200'),
        dict(event_ns='21000000',event_type='send',source_id='1',receiver_id='-1',sequence='0',payload_bytes='1200')]
    e.run();s=e.summary()
    assert s['terminal_counts']=={'success':1,'radio_not_received':1}
    assert s['opportunity_success_rate']==.5
    assert s['mean_success_latency_ms']==15


def test_receiver_replay_does_not_duplicate_datagrams():
    c=validate({"radio":"ns3","scenario":"static-pilot","sources":2,
                "duration_s":1,"warmup_s":0})
    e=NetworkReplay(c,1)
    receive=dict(event_ns='12000000',event_type='rx',source_id='0',receiver_id='1',sequence='0',payload_bytes='1200')
    e.radio_rows=[dict(receive,event_ns='11000000',event_type='send',receiver_id='-1'),receive,receive]
    e.run()
    assert len(e.terminals)==1
