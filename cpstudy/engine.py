"""Deterministic event harness for internal verification, not a radio simulator."""
import heapq
import itertools
import random
import math
from dataclasses import asdict
from collections import Counter
from .receiver import Receiver, Update
from .config import digest
from .metrics import opportunity_freshness, freshness_fraction

NS = 1_000_000_000


def ns(seconds):
    return round(seconds * NS)


class Engine:
    def __init__(self, cfg, seed):
        if cfg["radio"] != "ideal" or cfg["policy"] != "fixed":
            raise ValueError("Event harness supports fixed policy and ideal radio only; use network backend for adaptive claims")
        if cfg["clock_offset_ms"] != 0:
            raise ValueError("Clock-error observation model is not implemented yet")
        self.cfg, self.seed = cfg, seed
        self.events, self.logs, self.opportunities = [], [], []
        self.terminals, self.messages = {}, {}
        self.counter = itertools.count()
        self.receivers = []
        # A separate service RNG per receiver prevents unrelated arrival counts
        # from shifting the service sequence at other receivers.
        for r in range(cfg["sources"]):
            rng = random.Random(seed * 100003 + r)
            def service(u, rng=rng):
                mean = cfg["verify_ms"] * 1e6
                cv = cfg["service_cv"]
                if cv == 0: return round(mean)
                sigma = math.sqrt(math.log1p(cv**2))
                return max(0,round(rng.lognormvariate(math.log(mean)-sigma**2/2,sigma))) if mean else 0
            self.receivers.append(Receiver(r, cfg["queue_capacity"], round(cfg["verify_ms"]*1e6),
                                  round(cfg["fusion_ms"]*1e6), self.schedule,
                                  self.emit, self.terminal, service))

    def schedule(self, when, function, *args):
        heapq.heappush(self.events, (when, next(self.counter), function, args))

    def emit(self, when, event, u, depth=0, reason=None):
        if not hasattr(self,'_config_hash'):self._config_hash=digest(self.cfg)
        row=dict(run_id=f"{self._config_hash[:12]}-{self.seed}",
            config_hash=self._config_hash, seed=self.seed,
            scenario_id=self.cfg["scenario"],policy_id=self.cfg["policy"],
            source_id=u.source, receiver_id=u.receiver, opportunity_id=u.opportunity,
            message_id=u.message, object_ids=None, acquisition_ns=u.acquired,
            event_ns=when,event_type=event,payload_bytes=u.payload,wire_bytes=u.wire,
            queue_depth=depth,reason=reason)
        if hasattr(self,'log_sink'):self.log_sink(row)
        else:self.logs.append(row)

    def terminal(self, when, u, reason):
        key = (u.message,u.receiver)
        if key in self.terminals: raise AssertionError(f"Duplicate terminal {key}")
        self.terminals[key] = dict(at_ns=when,reason=reason,acquisition_ns=u.acquired,
                                   opportunity_id=u.opportunity,source_id=u.source)
        self.emit(when,"terminal",u,reason=reason)

    def acquire(self, when, source, i):
        c = self.cfg
        opportunity_id = f"{source}:{i}"
        deadline = when+round(c["deadline_ms"]*1e6)
        evaluated = ns(c["warmup_s"]) <= when and deadline <= ns(c["duration_s"])
        # Ideal harness uses all-to-all receiver eligibility, deliberately no
        # mobility/occlusion claim. This trace remains invariant to max_rate_hz.
        receivers = [r for r in range(c["sources"]) if r != source]
        row=dict(opportunity_id=opportunity_id,source_id=source,acquisition_ns=when,
                 deadline_ns=deadline,receiver_ids=receivers,evaluated=evaluated,
                 evaluation_basis="source update, not object-level perception")
        self.opportunities.append(row)
        # Deterministic admission on a common opportunity trace, one latest
        # acquisition per selected emission; no random thinning artifacts.
        due = self.messages.get(source,when)
        if when < due:
            row["generated"] = False
            return
        # Advance the target timeline, rather than rounding every interval up
        # to a sensing tick. Jitter is bounded by one sensing interval.
        self.messages[source] = due + ns(1/c["max_rate_hz"])
        row["generated"] = True
        for r in receivers:
            u = Update(source,r,opportunity_id,opportunity_id,when,deadline,
                       c["payload_bytes"],c["payload_bytes"]+c["security_bytes"])
            self.emit(when,"acquisition",u)
            generated = when+round((c["inference_ms"]+c["sign_ms"])*1e6)
            self.schedule(generated,self.transmit,u)

    def transmit(self, when, u):
        self.emit(when,"generation",u)
        self.emit(when,"transmission",u)
        self.schedule(when+round(self.cfg["ideal_delay_ms"]*1e6),
                      self.receivers[u.receiver].receive,u)

    def run(self):
        c=self.cfg
        rng=random.Random(self.seed)
        phases=[rng.randrange(ns(1/c["opportunity_hz"])) for _ in range(c["sources"])]
        for s in range(c["sources"]):
            i=0
            while True:
                t=phases[s]+ns(i/c["opportunity_hz"])
                if t>=ns(c["duration_s"]): break
                self.schedule(t,self.acquire,s,i);i+=1
        stop=ns(c["duration_s"])
        while self.events:
            t,_,fn,args=heapq.heappop(self.events)
            if t>stop: break
            fn(t,*args)
        # Censor only at the fixed observation boundary. This is not a success.
        for o in self.opportunities:
            if o["generated"]:
                for r in o["receiver_ids"]:
                    key=(o["opportunity_id"],r)
                    if key not in self.terminals:
                        u=Update(o["source_id"],r,o["opportunity_id"],o["opportunity_id"],
                                 o["acquisition_ns"],o["deadline_ns"],c["payload_bytes"],
                                 c["payload_bytes"]+c["security_bytes"])
                        self.terminal(stop,u,"processing_unfinished" if u.deadline<=stop else "right_censored")
        return self

    def summary(self):
        eligible=[o for o in self.opportunities if o["evaluated"]]
        denominator=sum(len(o["receiver_ids"]) for o in eligible)
        reasons=Counter(); latencies=[]; generated=0
        for o in eligible:
            for r in o["receiver_ids"]:
                if not o["generated"]:
                    reasons["suppressed"]+=1;continue
                generated+=1
                terminal=self.terminals[(o["opportunity_id"],r)]
                reasons[terminal["reason"]]+=1
                if terminal["reason"]=="success":
                    latencies.append((terminal["at_ns"]-o["acquisition_ns"])/1e6)
        fresh,external=opportunity_freshness(self.opportunities,self.terminals)
        streams={(s,r):[] for s in range(self.cfg["sources"]) for r in range(self.cfg["sources"]) if s!=r}
        for (_,r),t in self.terminals.items():
            if t["reason"]=="success":streams[(t["source_id"],r)].append((t["at_ns"],t["acquisition_ns"]))
        coverage=[freshness_fraction(events,ns(self.cfg["warmup_s"]),ns(self.cfg["duration_s"]),
                                   round(self.cfg["deadline_ms"]*1e6)) for events in streams.values()]
        return dict(backend="ideal internal harness",seed=self.seed,
             opportunity_receiver_pairs=denominator,generated_receiver_pairs=generated,
             terminal_counts=dict(reasons),opportunity_success_rate=reasons["success"]/denominator if denominator else None,
             generated_success_rate=reasons["success"]/generated if generated else None,
             mean_success_latency_ms=sum(latencies)/len(latencies) if latencies else None,
             fresh_opportunity_pairs=fresh,opportunity_freshness_rate=fresh/external if external else None,
             mean_time_freshness_fraction=sum(coverage)/len(coverage),
             excluded_opportunities=len(self.opportunities)-len(eligible),
             applicability="Internal accounting verification only; no radio or perception validation")
