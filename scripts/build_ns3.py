"""Build the pinned radio pilot without changing system packages.

Run with the project venv after installing requirements.lock.txt.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
VERSION='3.46.1'
URL=f'https://www.nsnam.org/releases/ns-{VERSION}.tar.bz2'
SHA1='a02ce48bf2cb46ab8bcc0da10e47bfca1e13cdf3'
SHA256='fd3255df035a52008638fb5d81f77685260fd607be107eaf8e5116bcf1fd2c03'


def main():
    p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=4)
    p.add_argument('--cache',type=Path,default=Path.home()/'.cache/cpstudy-toolchains')
    a=p.parse_args()
    if a.jobs<1:p.error('--jobs must be positive')
    a.cache.mkdir(parents=True,exist_ok=True)
    archive=a.cache/f'ns-{VERSION}.tar.bz2'
    if not archive.exists():
        partial=archive.with_suffix('.partial')
        urllib.request.urlretrieve(URL,partial);partial.rename(archive)
    blob=archive.read_bytes()
    if hashlib.sha1(blob).hexdigest()!=SHA1 or hashlib.sha256(blob).hexdigest()!=SHA256:
        raise SystemExit('Archive hash mismatch; refusing extraction')
    source=a.cache/f'ns-{VERSION}'
    if not source.exists():
        with tarfile.open(archive) as tar:tar.extractall(a.cache,filter='data')
    shutil.copy2(ROOT/'simulator/cp-radio-pilot.cc',source/'scratch/cp-radio-pilot.cc')
    shutil.copy2(ROOT/'simulator/cp-closed-loop.cc',source/'scratch/cp-closed-loop.cc')
    env=os.environ.copy();env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    commands=[('ns3-configure.log',[sys.executable,'ns3','configure',
        '--enable-modules=wifi,mobility,internet,applications','--enable-examples',
        '--enable-tests','--build-profile=release']),
        ('ns3-build.log',[sys.executable,'ns3','build','cp-radio-pilot','-j',str(a.jobs)])]
    commands.append(('ns3-closed-loop-build.log',[sys.executable,'ns3','build','cp-closed-loop','-j',str(a.jobs)]))
    for log,cmd in commands:
        print('Running',cmd,flush=True)
        with (evidence/log).open('w') as f:
            result=subprocess.run(cmd,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT)
        if result.returncode:raise SystemExit(f'Build failed; inspect {evidence/log}')
    record=dict(version='ns-'+VERSION,source_url=URL,published_sha1=SHA1,
                sha256=SHA256,local_source=str(source),
                pilot_sha256=hashlib.sha256((source/'scratch/cp-radio-pilot.cc').read_bytes()).hexdigest())
    record['closed_loop_sha256']=hashlib.sha256((source/'scratch/cp-closed-loop.cc').read_bytes()).hexdigest()
    (evidence/'ns3_source.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Pinned radio pilot build completed')


if __name__=='__main__':main()
