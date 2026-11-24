"""Exercise mobility, policy isolation and causal feedback on the real binary."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
import yaml


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    reports=[]
    for scenario in ['intersection','highway']:
        reference=None
        for policy in ['fixed','radio','receiver','joint','dcc']:
            config=dict(radio='ns3-closed-loop',scenario=scenario,policy=policy,sources=16,
              duration_s=4.,warmup_s=.5,verify_ms=3.,feedback_ms=500.,feedback_stale_ms=1500.,
              output=str(args.output/scenario/policy))
            path=args.output/(scenario+'-'+policy+'.yaml');path.write_text(yaml.safe_dump(config))
            result=subprocess.run([sys.executable,'-m','cpstudy','run','--config',str(path),'--seed','23'],
                                  capture_output=True,text=True,check=True)
            manifest=Path(result.stdout.strip());root=manifest.parent
            audit=subprocess.run([sys.executable,'-m','cpstudy','audit','--manifest',str(manifest)],
                                 capture_output=True,text=True,check=True)
            opportunities=[json.loads(x) for x in gzip.open(root/'opportunities.jsonl.gz','rt')]
            demand=[{k:o[k] for k in ('opportunity_id','acquisition_ns','deadline_ns','receiver_ids','source_x','source_y')}
                    for o in opportunities]
            if reference is None:reference=demand
            elif demand!=reference:raise AssertionError('Policy changed external demand: '+scenario+' '+policy)
            summary=json.loads((root/'summary.json').read_text())
            if policy in ('receiver','joint'):
                if summary['feedback_datagrams_sent']<=0:raise AssertionError('Missing receiver feedback')
            elif summary['feedback_datagrams_sent']!=0:raise AssertionError('Unexpected baseline feedback')
            reports.append(dict(scenario=scenario,policy=policy,manifest=str(manifest),audit=json.loads(audit.stdout),summary=summary))
    (args.output/'report.json').write_text(json.dumps(dict(shared_exogenous_demand=True,runs=reports),indent=2)+'\n')
    print('All 10 mobility/policy runs passed common-demand and independent causal audits')


if __name__=='__main__':main()
