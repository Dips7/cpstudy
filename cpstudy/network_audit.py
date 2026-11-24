"""Independent replay of receiver-feedback visibility and controller decisions."""
import csv
import gzip
import heapq
import math
from .policy import Controller
from .dcc import AdaptiveDcc,airtime_s


def read_csv(path):
    with gzip.open(path,'rt') as f:yield from csv.DictReader(f)


def ordered_rows(path,kind):
    previous=-1
    for row in read_csv(path):
        order=int(row['trace_order'])
        if order<=previous:raise ValueError('Non-increasing raw trace order')
        previous=order
        yield order,kind,row


def audit_network(root,cfg):
    streams=[ordered_rows(root/'network-events.csv.gz','event'),ordered_rows(root/'network-controls.csv.gz','control')]
    dcc=[AdaptiveDcc() for _ in range(cfg['sources'])]
    dcc_rates=[min(cfg['max_rate_hz'],1/min(1.,max(.025,airtime_s(cfg['payload_bytes']+cfg['security_bytes'])/.005)))
               for _ in dcc]
    if cfg['policy']=='dcc':
        streams.append(ordered_rows(root/'network-dcc.csv.gz','dcc'))
    merged=heapq.merge(*streams,key=lambda x:x[0])
    states=[Controller(cfg['max_rate_hz']) for _ in range(cfg['sources'])]
    feedback=[{} for _ in states];verified=set();checked=0;previous_time=-1;previous_order=-1
    for order,kind,row in merged:
        if order==previous_order:raise ValueError('Duplicate raw trace ordinal')
        previous_order=order
        now=int(row['event_ns'])
        if now<previous_time:raise ValueError('Noncausal raw network trace')
        previous_time=now
        if kind=='event':
            if row['kind']!='1':continue
            key=(int(row['source_id']),int(row['receiver_id']),int(row['sequence']))
            if row['event_type']=='feedback_acquisition':
                if int(row['reported_backlog'])!=int(row['queue_depth']):
                    raise ValueError('Feedback snapshot disagrees with local queue observation')
            elif row['event_type']=='verification_end':verified.add(key)
            elif row['event_type']=='terminal' and row['reason']=='feedback_ready':
                if key not in verified:raise ValueError('Feedback became observable before verification')
                verified.discard(key)
                source,receiver,_=key;acquired=int(row['acquisition_ns'])
                old=feedback[receiver].get(source)
                if old is None or old[0]<acquired:
                    feedback[receiver][source]=(acquired,int(row['reported_backlog']))
        elif kind=='dcc':
            node=int(row['node_id'])
            rate=dcc[node].update(float(row['current_busy']),float(row['previous_busy']),
                                 cfg['payload_bytes']+cfg['security_bytes'],cfg['max_rate_hz'])
            for expected,actual in [(rate,float(row['rate_hz'])),(dcc[node].delta,float(row['delta'])),
                                    (dcc[node].estimate,float(row['smoothed_busy']))]:
                if not math.isclose(expected,actual,rel_tol=1e-12,abs_tol=1e-12):
                    raise ValueError('DCC update differs from independent reference')
            dcc_rates[node]=rate
        else:
            node=int(row['node_id'])
            current=[depth for acquired,depth in feedback[node].values()
                     if now-acquired<=round(cfg['feedback_stale_ms']*1e6)]
            backlog=max(current,default=0);stale=not current
            busy=float(row['busy_fraction'])
            if not 0<=busy<=1:raise ValueError('Occupied channel fraction outside [0,1]')
            if int(row['observed_neighbors'])!=len(current) or bool(int(row['feedback_stale']))!=stale:
                raise ValueError('Controller accessed unavailable receiver feedback')
            if float(row['remote_backlog'])!=backlog:raise ValueError('Remote backlog mismatch')
            avg_backlog=(sum(current)/len(current)) if current else 0.0
            rate=dcc_rates[node] if cfg['policy']=='dcc' else states[node].update(cfg,busy,backlog,stale=stale,observed=len(current),avg_backlog=avg_backlog)
            if not math.isclose(rate,float(row['rate_hz']),rel_tol=1e-12,abs_tol=1e-12):
                raise ValueError('C++ controller differs from independent Python controller')
            checked+=1
    return dict(control_decisions_checked=checked,feedback_visibility='verified causal replay')
