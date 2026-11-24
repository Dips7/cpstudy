"""Reproduce the ns-3 pilot and test receiver overload on real radio traces."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    base=dict(scenario='static-pilot',radio='ns3',policy='fixed',sources=2,
              duration_s=2.,warmup_s=.2,opportunity_hz=10.,max_rate_hz=10.)
    def run(name,cfg):
        cfg=cfg|{'output':str(args.output/name)}
        config=args.output/(name+'.yaml');config.write_text(yaml.safe_dump(cfg))
        result=subprocess.run([sys.executable,'-m','cpstudy','run','--config',str(config),'--seed','17'],
                              check=True,capture_output=True,text=True)
        manifest=Path(result.stdout.strip());root=manifest.parent
        audit=subprocess.run([sys.executable,'-m','cpstudy','audit','--manifest',str(manifest)],
                             check=True,capture_output=True,text=True)
        return root,json.loads((root/'summary.json').read_text()),json.loads(audit.stdout)
    a,sa,aa=run('repeat-a',base);b,sb,ab=run('repeat-b',base)
    if sa!=sb:raise AssertionError('Same-seed summary mismatch')
    for file in ['radio.csv','events.jsonl.gz','opportunities.jsonl.gz']:
        read=lambda p:gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
        if read(a/file)!=read(b/file):raise AssertionError('Same-seed trace mismatch: '+file)
    c,sc,ac=run('receiver-overload',base|dict(sources=10,duration_s=3.,warmup_s=.5,verify_ms=30.))
    if sc['opportunity_success_rate']>=sa['opportunity_success_rate']:
        raise AssertionError('Receiver overload did not reduce timely coverage')
    if sc['terminal_counts'].get('right_censored',0):
        raise AssertionError('Observed deadline misses mislabeled censored')
    report=dict(same_seed_radio_and_receiver_traces_identical=True,
        low_load_summary=sa,overloaded_summary=sc,
        audits=[aa,ab,ac],manifests=[str(p/'manifest.json') for p in [a,b,c]],
        caveat='Pilot correctness checks; no deployed-vehicle calibration or adaptive-policy result')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
