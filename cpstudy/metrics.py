"""Source-update freshness from authenticated fusion-ready traces.

No detection accuracy, object coverage or safety interpretation is implied.
"""
from bisect import bisect_right


def opportunity_freshness(opportunities, terminals):
    """A newer authenticated observation can satisfy an older demand.

    Arrival after the queried deadline cannot satisfy it. Missing/suppressed
    messages stay in the demand denominator. Returns success and total counts.
    """
    streams={}
    for (message,receiver), t in terminals.items():
        if t["reason"]=="success":
            streams.setdefault((t["source_id"],receiver),[]).append((t["at_ns"],t["acquisition_ns"]))
    indexes={}
    for key,events in streams.items():
        events.sort();times=[];latest=[];maximum=-1
        for ready,acquired in events:
            maximum=max(maximum,acquired);times.append(ready);latest.append(maximum)
        indexes[key]=(times,latest)
    successes=total=0
    for o in opportunities:
        if not o["evaluated"]:continue
        for receiver in o["receiver_ids"]:
            total+=1;times,latest=indexes.get((o["source_id"],receiver),([],[]))
            i=bisect_right(times,o["deadline_ns"])-1
            if i>=0 and latest[i]>=o["acquisition_ns"]:successes+=1
    return successes,total


def freshness_fraction(events, start, stop, age_limit):
    """Exact time fraction with at least one valid update and age <= limit.

    events contains (fusion_ready_ns, acquired_ns). Before first authenticated
    update, coverage is zero. Earlier acquisition timestamps cannot regress age.
    """
    if stop<=start or age_limit<0:raise ValueError("Invalid observation window")
    latest=None;cursor=start;covered=0
    for ready,acquired in sorted(events)+[(stop,-1)]:
        if ready<start:
            latest=acquired if latest is None else max(latest,acquired);continue
        end=min(ready,stop)
        if latest is not None:
            covered+=max(0,min(end,latest+age_limit)-cursor)
        cursor=end
        if ready>=stop:break
        latest=acquired if latest is None else max(latest,acquired)
    return covered/(stop-start)
