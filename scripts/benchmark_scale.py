"""Measure one larger workload before allocating the research campaign."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import yaml


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sources',type=int,default=60);p.add_argument('--duration',type=float,default=12.)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    config=dict(radio='ns3-closed-loop',scenario='intersection',sources=args.sources,
                duration_s=args.duration,warmup_s=2.,policy='fixed',verify_ms=1.,
                output=str(args.output/'run'))
    path=args.output/'config.yaml';path.write_text(yaml.safe_dump(config))
    start=time.perf_counter()
    result=subprocess.run([sys.executable,'-m','cpstudy','run','--config',str(path),'--seed','31'],
                          capture_output=True,text=True,check=True)
    elapsed=time.perf_counter()-start;manifest=Path(result.stdout.strip())
    audit=subprocess.run([sys.executable,'-m','cpstudy','audit','--manifest',str(manifest)],
                         capture_output=True,text=True,check=True)
    usage=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    report=dict(sources=args.sources,simulated_seconds=args.duration,wall_seconds=elapsed,
        output_bytes=sum(p.stat().st_size for p in manifest.parent.iterdir() if p.is_file()),
        max_child_rss_bytes=usage if sys.platform=='darwin' else usage*1024,
        memory_note='OS child-process peak statistic; not sum of simultaneous process RSS',
        manifest=str(manifest),audit=json.loads(audit.stdout),
        caution='Pilot resource estimate; do not linearly extrapolate across density or overload')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
