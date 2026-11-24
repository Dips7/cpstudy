import argparse
import gzip
import hashlib
import json
import platform
from pathlib import Path
import sys
import time
from .config import load, digest
from .engine import Engine
from .metrics import opportunity_freshness
from .radio import NetworkReplay
from .closed_loop import ClosedLoop
from .network_audit import audit_network


def dump(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def records(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt') as f:
        for line in f:yield json.loads(line)


def run(args):
    if args.seed<1:raise ValueError('seed must be a positive integer')
    cfg=load(args.config)
    target=Path(cfg["output"])/f"{digest(cfg)[:12]}-seed{args.seed}"
    if target.exists(): raise ValueError(f"Refusing to overwrite run: {target}")
    source_files=sorted(list(Path('cpstudy').glob('*.py'))+list(Path('simulator').glob('*.cc'))+
                        list(Path('scripts').glob('*.py'))+[Path('requirements.lock.txt'),Path('pyproject.toml')])
    source_hashes={str(p):sha(p) for p in source_files}
    start=time.perf_counter()
    network=cfg['radio'] in ('ns3','ns3-closed-loop')
    if network:
        cls=NetworkReplay if cfg['radio']=='ns3' else ClosedLoop
        engine=cls(cfg,args.seed).run_radio(target).run()
    else:
        engine=Engine(cfg,args.seed).run()
        target.mkdir(parents=True)
    dump(target/"config.json",cfg)
    if any(sha(p)!=expected for p,expected in source_hashes.items()):
        raise ValueError('Research implementation changed during the run; do not use this run')
    dump(target/"summary.json",engine.summary())
    for name,rows in (("events.jsonl.gz",engine.logs),("opportunities.jsonl.gz",engine.opportunities)):
        if name=='events.jsonl.gz' and getattr(engine,'event_file_written',False):continue
        with gzip.open(target/name,"wt") as f:
            for row in rows:f.write(json.dumps(row,allow_nan=False)+"\n")
    files=["config.json","summary.json","events.jsonl.gz","opportunities.jsonl.gz"]
    if cfg["radio"]=="ns3":files += ["radio.csv","radio-process.log"]
    if cfg['radio']=='ns3-closed-loop':
        files += ['radio-process.log']+[p.name for p in sorted(target.glob('network-*.csv.gz'))]
    dump(target/"manifest.json",dict(schema_version=1,config_hash=digest(cfg),seed=args.seed,
         wall_seconds=time.perf_counter()-start,python=sys.version,platform=platform.platform(),
         source_hashes=source_hashes,
         radio_binary_sha256=engine.executed_binary_sha256 if network else None,
         files={p:sha(target/p) for p in files}))
    print(target/"manifest.json")


def audit(args):
    manifest=Path(args.manifest);m=json.loads(manifest.read_text());root=manifest.parent
    for name,expected in m["files"].items():
        if sha(root/name)!=expected:raise ValueError(f"File hash mismatch: {name}")
    cfg=json.loads((root/"config.json").read_text())
    if digest(cfg)!=m["config_hash"]:raise ValueError("Config identity mismatch")
    opportunities=list(records(root/next(name for name in m['files'] if name.startswith('opportunities.jsonl'))))
    terminals={};ready=set()
    for e in records(root/next(name for name in m['files'] if name.startswith('events.jsonl'))):
        key=(e["message_id"],e["receiver_id"])
        if e["event_type"]=="verification_end":ready.add(key)
        if e["event_type"]=="fusion_ready" and key not in ready:
            raise ValueError("Fusion before authentication")
        if e["event_type"]=="terminal":
            if key in terminals:raise ValueError("Duplicate terminal")
            terminals[key]=e
    expected={(o["opportunity_id"],r) for o in opportunities if o["generated"] for r in o["receiver_ids"]}
    if set(terminals)!=expected:raise ValueError("Missing or unexpected message terminal")
    denominator=sum(len(o["receiver_ids"]) for o in opportunities if o["evaluated"])
    reasons={};success_latency=[];generated=0
    for o in opportunities:
        if not o["evaluated"]:continue
        for r in o["receiver_ids"]:
            if o["generated"]:
                generated+=1;e=terminals[(o["opportunity_id"],r)];reason=e["reason"]
                if reason=="success":
                    if e["event_ns"]>o["deadline_ns"]:raise ValueError("Late success")
                    success_latency.append((e["event_ns"]-o["acquisition_ns"])/1e6)
            else:reason="suppressed"
            reasons[reason]=reasons.get(reason,0)+1
    summary=json.loads((root/"summary.json").read_text())
    if denominator!=summary["opportunity_receiver_pairs"] or reasons!=summary["terminal_counts"]:
        raise ValueError("Summary disagrees with independently recounted events")
    if sum(reasons.values())!=denominator:raise ValueError("Opportunity conservation failed")
    if generated!=summary["generated_receiver_pairs"]:raise ValueError("Generated count mismatch")
    values={(e["message_id"],e["receiver_id"]):dict(reason=e["reason"],at_ns=e["event_ns"],
        acquisition_ns=e["acquisition_ns"],source_id=e["source_id"]) for e in terminals.values()}
    fresh,total=opportunity_freshness(opportunities,values)
    if fresh!=summary["fresh_opportunity_pairs"]:raise ValueError("Freshness coverage mismatch")
    scalar_checks={
        'opportunity_success_rate':reasons.get('success',0)/denominator if denominator else None,
        'generated_success_rate':reasons.get('success',0)/generated if generated else None,
        'opportunity_freshness_rate':fresh/total if total else None,
        'mean_success_latency_ms':sum(success_latency)/len(success_latency) if success_latency else None,
    }
    for key,value in scalar_checks.items():
        if summary[key]!=value:raise ValueError(f'Summary metric mismatch: {key}')
    network_check=audit_network(root,cfg) if cfg['radio']=='ns3-closed-loop' else None
    print(json.dumps(dict(audit="passed",message_receiver_pairs=len(expected),
                         evaluated_opportunity_receiver_pairs=denominator,terminal_counts=reasons,
                         network_check=network_check)))


def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="command",required=True)
    v=s.add_parser("validate-config");v.add_argument("config")
    r=s.add_parser("run");r.add_argument("--config",required=True);r.add_argument("--seed",type=int,required=True)
    a=s.add_parser("audit");a.add_argument("--manifest",required=True)
    c=s.add_parser("campaign");c.add_argument("--manifest",required=True);c.add_argument("--jobs",type=int,default=4)
    an=s.add_parser("analyze");an.add_argument("--manifest",required=True)
    f=s.add_parser("figures");f.add_argument("--manifest",required=True)
    args=p.parse_args()
    try:
        if args.command=="validate-config":print(json.dumps(load(args.config),indent=2))
        elif args.command=="run":run(args)
        elif args.command=="audit":audit(args)
        elif args.command=="campaign":
            from .campaign import run_campaign
            run_campaign(args.manifest,max_workers=args.jobs)
        elif args.command=="analyze":
            from .campaign import analyze_campaign
            analyze_campaign(args.manifest)
        elif args.command=="figures":
            from .campaign import generate_figures
            generate_figures(args.manifest)
    except (ValueError,OSError,KeyError,RuntimeError) as e:
        p.exit(1,f"error: {e}\n")


if __name__=="__main__":main()
