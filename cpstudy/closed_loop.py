"""Import the closed-loop ns-3 experiment into the common audit contract."""
import csv
import hashlib
import gzip
import json
from pathlib import Path
import subprocess
from .engine import Engine,ns
from .receiver import Update

ARGUMENTS=("sources","duration_s","warmup_s","opportunity_hz","max_rate_hz","min_rate_hz",
    "deadline_ms","inference_ms","sign_ms","verify_ms","fusion_ms","queue_capacity",
    "payload_bytes","security_bytes","feedback_bytes","control_ms","feedback_ms","feedback_stale_ms",
    "radio_high","radio_low","queue_high","queue_low","decrease","increase_hz","service_cv",
    "range_m","speed_mps","policy","scenario","matched_feedback")


class ClosedLoop(Engine):
    def __init__(self,cfg,seed):
        if cfg['scenario'] not in ('intersection','highway'):
            raise ValueError('Closed-loop backend requires a mobility scenario')
        if cfg['clock_offset_ms']!=0:
            raise ValueError('Nonzero clock observations remain unsupported')
        if min(cfg['payload_bytes']+cfg['security_bytes'],cfg['feedback_bytes']+cfg['security_bytes'])<24:
            raise ValueError('Application datagram must include its 24-byte experiment header')
        self.cfg,self.seed=cfg,seed
        self.logs=[];self.opportunities=[];self.terminals={}

    def run_radio(self,output):
        record=json.loads(Path('evidence/ns3_source.json').read_text())
        if record.get('closed_loop_sha256')!=hashlib.sha256(Path('simulator/cp-closed-loop.cc').read_bytes()).hexdigest():
            raise ValueError('Workspace simulator source differs from pinned build; rebuild before running')
        binaries=list((Path(record['local_source'])/'build/scratch').glob('ns3.46.1-cp-closed-loop'))
        if len(binaries)!=1:raise ValueError('Build cp-closed-loop with scripts/build_ns3.py first')
        self.radio_binary=binaries[0]
        self.executed_binary_sha256=hashlib.sha256(self.radio_binary.read_bytes()).hexdigest()
        output.mkdir(parents=True,exist_ok=False)
        args=[str(self.radio_binary),f'--seed={self.seed}',f'--output={output}']
        args.extend(f'--{k}={int(self.cfg[k]) if isinstance(self.cfg[k],bool) else self.cfg[k]}' for k in ARGUMENTS)
        result=subprocess.run(args,capture_output=True,text=True)
        if hashlib.sha256(self.radio_binary.read_bytes()).hexdigest()!=self.executed_binary_sha256:
            raise ValueError('Simulator binary changed during run; discard this run and retry after build completion')
        (output/'radio-process.log').write_text(result.stdout+result.stderr)
        if result.returncode:raise ValueError(f'Closed-loop simulator failed: {result.returncode}; see {output}')
        self.directory=output
        return self

    def run(self):
        c=self.cfg;updates={};by_id={}
        log_file=gzip.open(self.directory/'events.jsonl.gz','wt')
        self.log_sink=lambda row:log_file.write(json.dumps(row,allow_nan=False)+'\n')
        with (self.directory/'network-opportunities.csv').open() as f:
            for row in csv.DictReader(f):
                source=int(row['source_id']);oid=f"{source}:{row['sequence']}"
                receivers=[int(r) for r in row['receiver_ids'].split('|') if r]
                acquired=int(row['acquisition_ns']);deadline=int(row['deadline_ns'])
                o=dict(opportunity_id=oid,source_id=source,acquisition_ns=acquired,
                    deadline_ns=deadline,receiver_ids=receivers,generated=row['generated']=='1',
                    evaluated=ns(c['warmup_s'])<=acquired and deadline<=ns(c['duration_s']),
                    source_x=float(row['x']),source_y=float(row['y']),
                    evaluation_basis='source-update freshness for geometrically eligible receiver pairs')
                self.opportunities.append(o);by_id[oid]=o
                if o['generated']:
                    for r in receivers:
                        u=Update(source,r,oid,oid,acquired,deadline,c['payload_bytes'],c['payload_bytes']+c['security_bytes'])
                        updates[(oid,r)]=u;self.emit(acquired,'acquisition',u)
        received=set();sent=set();feedback_sent=feedback_received=feedback_verified=0
        with (self.directory/'network-events.csv').open() as f:
            for row in csv.DictReader(f):
                kind=int(row['kind']);event=row['event_type']
                if kind:
                    feedback_sent+=event=='transmission'
                    feedback_received+=event=='reception'
                    feedback_verified+=event=='verification_end'
                    continue
                oid=f"{row['source_id']}:{row['sequence']}";when=int(row['event_ns'])
                if event=='transmission':
                    sent.add(oid)
                    for r in by_id[oid]['receiver_ids']:
                        u=updates[(oid,r)];self.emit(when,'generation',u)
                        self.emit(when,'transmission',u,reason=row['reason'])
                    continue
                key=(oid,int(row['receiver_id']))
                if key not in updates:continue # Noneligible traffic still used simulated CPU/radio.
                u=updates[key]
                if event=='reception':received.add(key)
                if event=='terminal':self.terminal(when,u,row['reason'])
                else:self.emit(when,event,u,int(row['queue_depth']))
        stop=ns(c['duration_s'])
        for key,u in updates.items():
            if key not in self.terminals:
                if u.deadline>stop:reason='right_censored'
                elif key in received:reason='processing_unfinished'
                elif u.message not in sent:reason='sender_unfinished'
                else:reason='radio_not_received'
                self.terminal(stop,u,reason)
        self.extra=dict(feedback_datagrams_sent=feedback_sent,feedback_receptions=feedback_received,
                        feedback_verifications=feedback_verified)
        log_file.close();del self.log_sink
        self.event_file_written=True
        for path in self.directory.glob('network-*.csv'):
            with path.open('rb') as source,gzip.open(str(path)+'.gz','wb') as target:
                import shutil
                shutil.copyfileobj(source,target)
            path.unlink() # Only this run's generated uncompressed intermediate.
        return self

    def summary(self):
        s=super().summary()
        s.pop('mean_time_freshness_fraction') # Eligibility is time varying in mobility experiments.
        s.update(self.extra)
        s['backend']='ns-3.46.1 closed-loop 802.11p PHY/AdhocWifiMac with synthetic mobility'
        s['applicability']='Source-update timeliness; no CPM conformance, perception accuracy, or calibrated road safety claim'
        s['feedback_used_after_verification']=True
        return s
