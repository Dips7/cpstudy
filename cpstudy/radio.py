"""Fixed-workload ns-3 pilot and offline receiver replay.

Offline replay is causal only while receiver processing does not feed back into
radio transmissions. Adaptive policies require a closed-loop simulator instead.
"""
import csv
import hashlib
import heapq
import json
from pathlib import Path
import subprocess
from .engine import Engine, ns
from .receiver import Update


class NetworkReplay(Engine):
    def __init__(self,cfg,seed):
        if cfg["policy"]!="fixed" or cfg["scenario"]!="static-pilot":
            raise ValueError("Network pilot supports fixed policy and static-pilot scenario only")
        if cfg["opportunity_hz"]!=cfg["max_rate_hz"]:
            raise ValueError("Fixed pilot replay requires equal acquisition and emission rates")
        if cfg["inference_ms"]+cfg["sign_ms"]!=11:
            raise ValueError("Network pilot currently pins inference + signing at 11 ms")
        super().__init__(cfg|{"radio":"ideal"},seed)
        self.cfg=cfg

    def run_radio(self,output):
        record=json.loads(Path('evidence/ns3_source.json').read_text())
        source=Path(record['local_source'])
        binaries=list((source/'build/scratch').glob('ns3.46.1-cp-radio-pilot*'))
        binaries=[p for p in binaries if p.is_file() and p.suffix not in ('.cc','.o')]
        if len(binaries)!=1:raise ValueError("Build the pinned ns-3 cp-radio-pilot first")
        self.radio_binary=binaries[0]
        self.executed_binary_sha256=hashlib.sha256(self.radio_binary.read_bytes()).hexdigest()
        output.mkdir(parents=True,exist_ok=False)
        args=[str(self.radio_binary),f'--sources={self.cfg["sources"]}',
              f'--duration={self.cfg["duration_s"]}',f'--rate={self.cfg["max_rate_hz"]}',
              f'--bytes={self.cfg["payload_bytes"]+self.cfg["security_bytes"]}',
              f'--seed={self.seed}',f'--output={output/"radio.csv"}']
        result=subprocess.run(args,capture_output=True,text=True)
        if hashlib.sha256(self.radio_binary.read_bytes()).hexdigest()!=self.executed_binary_sha256:
            raise ValueError('Radio binary changed during run')
        (output/'radio-process.log').write_text(result.stdout+result.stderr)
        if result.returncode:raise ValueError(f"ns-3 pilot failed: {result.returncode}; see {output}")
        self.radio_rows=list(csv.DictReader((output/'radio.csv').open()))
        return self

    def run(self):
        c=self.cfg;updates={}
        # Build the immutable source schedule from send events, then replay
        # actual reception events. All intended receiver pairs include loss.
        for row in self.radio_rows:
            if row['event_type']!='send':continue
            source=int(row['source_id']);i=int(row['sequence']);t=int(row['event_ns'])
            acquired=t-11_000_000;deadline=acquired+round(c['deadline_ms']*1e6)
            oid=f'{source}:{i}';receivers=[r for r in range(c['sources']) if r!=source]
            self.opportunities.append(dict(opportunity_id=oid,source_id=source,
                acquisition_ns=acquired,deadline_ns=deadline,receiver_ids=receivers,
                evaluated=ns(c['warmup_s'])<=acquired and deadline<=ns(c['duration_s']),
                generated=True,evaluation_basis='source update in static radio pilot'))
            for r in receivers:
                u=Update(source,r,oid,oid,acquired,deadline,c['payload_bytes'],int(row['payload_bytes']))
                updates[(oid,r)]=u
                self.emit(acquired,'acquisition',u);self.emit(t,'generation',u);self.emit(t,'transmission',u)
        receptions=set()
        for row in self.radio_rows:
            if row['event_type']!='rx':continue
            source=int(row['source_id']);r=int(row['receiver_id']);i=int(row['sequence']);t=int(row['event_ns'])
            key=(f'{source}:{i}',r)
            if key not in updates:raise ValueError(f'Unexpected receive {key}')
            if key in receptions:continue  # Duplicate datagrams cannot enqueue twice.
            receptions.add(key)
            self.schedule(t,self.receivers[r].receive,updates[key])
        stop=ns(c['duration_s'])
        while self.events:
            t,_,fn,args=heapq.heappop(self.events)
            if t>stop:break
            fn(t,*args)
        for key,u in updates.items():
            if key not in self.terminals:
                reason='radio_not_received' if key not in receptions and u.deadline<=stop else 'right_censored'
                # A received update still pending at its deadline is a miss,
                # even if processing is administratively censored at run end.
                if key in receptions and u.deadline<=stop:reason='processing_unfinished'
                self.terminal(stop,u,reason)
        return self

    def summary(self):
        result=super().summary()
        result['backend']='ns-3.46.1 static 802.11p PHY + AdhocWifiMac; offline verification replay'
        result['applicability']='Radio pilot only; no mobility, standards conformance, or policy improvement claim'
        return result
