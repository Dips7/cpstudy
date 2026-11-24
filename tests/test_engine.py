import json
import subprocess
import sys
from cpstudy.config import validate
from cpstudy.engine import Engine


def test_ideal_latency_and_conservation():
    c=validate({"sources":2,"duration_s":1,"warmup_s":0})
    result=Engine(c,3).run();s=result.summary()
    assert s["opportunity_success_rate"]==1
    assert s["mean_success_latency_ms"]==15
    assert sum(s["terminal_counts"].values())==s["opportunity_receiver_pairs"]
    assert sum(s["terminal_counts"].values())==s["generated_receiver_pairs"]


def test_suppression_never_removes_demand():
    base=validate({"sources":2,"duration_s":2,"warmup_s":0})
    a=Engine(base,1).run();b=Engine(base|{"max_rate_hz":1},1).run()
    assert a.summary()["opportunity_receiver_pairs"]==b.summary()["opportunity_receiver_pairs"]
    assert a.summary()["opportunity_success_rate"] > b.summary()["opportunity_success_rate"]
    assert b.summary()["generated_success_rate"]==1
    s=b.summary()
    suppressed_pairs=sum(len(o["receiver_ids"]) for o in b.opportunities
                         if o["evaluated"] and not o["generated"])
    generated_pairs=sum(len(o["receiver_ids"]) for o in b.opportunities
                        if o["evaluated"] and o["generated"])
    assert suppressed_pairs+generated_pairs==s["opportunity_receiver_pairs"]
    assert generated_pairs==s["generated_receiver_pairs"]
    assert sum(s["terminal_counts"].values())==generated_pairs
    keys=lambda e:[(o["opportunity_id"],o["acquisition_ns"],o["receiver_ids"]) for o in e.opportunities]
    assert keys(a)==keys(b)


def test_determinism_and_receiver_overload():
    c=validate({"sources":10,"duration_s":2,"warmup_s":0,"verify_ms":30})
    a=Engine(c,1).run();b=Engine(c,1).run()
    assert a.logs==b.logs
    assert a.summary()["opportunity_success_rate"]<1


def test_fully_observed_deadline_is_a_miss_not_boundary_censoring():
    c=validate({"sources":10,"duration_s":2,"warmup_s":0,"verify_ms":30})
    e=Engine(c,1).run()
    assert e.summary()['terminal_counts'].get('right_censored',0)==0


def test_non_divisor_rate_preserves_requested_average():
    c=validate({"sources":2,"duration_s":10,"warmup_s":0,"max_rate_hz":3})
    e=Engine(c,1).run()
    counts=[sum(o["generated"] for o in e.opportunities if o["source_id"]==s) for s in range(2)]
    assert counts==[30,30]


def test_cli_audit_and_tamper_rejection(tmp_path):
    import yaml
    cfg=tmp_path/"pilot.yaml";cfg.write_text(yaml.safe_dump({"sources":2,"duration_s":1,"warmup_s":0,"output":str(tmp_path/"runs")}))
    call=lambda *args:subprocess.run([sys.executable,"-m","cpstudy",*args],capture_output=True,text=True)
    run=call("run","--config",str(cfg),"--seed","1");assert run.returncode==0,run.stderr
    manifest=run.stdout.strip()
    assert call("audit","--manifest",manifest).returncode==0
    summary=__import__('pathlib').Path(manifest).parent/"summary.json"
    summary.write_text('{}')
    assert call("audit","--manifest",manifest).returncode!=0
