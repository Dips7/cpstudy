"""Independent Lindley-recursion checks against analytical M/G/1 means.

Run from the project root. Synthetic queue calibration, not vehicle measurements.
"""
import csv
import json
from pathlib import Path
import numpy as np
from scipy.stats import t as student_t
from cpstudy.model import mg1, muhammad2019_mean


def simulate(rate, mean, cv, seed, count=150000, warmup=10000):
    rng=np.random.default_rng(seed)
    gaps=rng.exponential(1/rate,count)
    services=(np.full(count,mean) if cv==0 else rng.exponential(mean,count))
    wait=0.;total=0.;seen=0
    for i in range(count):
        if i:wait=max(0,wait+services[i-1]-gaps[i])
        if i>=warmup:total+=wait+services[i];seen+=1
    return total/seen


def main():
    out=Path('results/processed/queue-validation');out.mkdir(parents=True,exist_ok=True)
    rows=[];raw=[]
    for cv in [0,1]:
        for rho in [.1,.4,.7,.9]:
            mean=.001;rate=rho/mean
            predicted=mg1(rate,mean,mean**2*(1+cv**2)).mean_sojourn_s
            values=[simulate(rate,mean,cv,seed) for seed in range(1,21)]
            raw.extend(dict(service_cv=cv,rho=rho,seed=seed,mean_sojourn_s=value)
                       for seed,value in enumerate(values,1))
            observed=float(np.mean(values));se=float(np.std(values,ddof=1)/np.sqrt(len(values)))
            rows.append(dict(service_cv=cv,rho=rho,predicted_s=predicted,
                 simulated_mean_s=observed,run_se_s=se,relative_error=abs(observed-predicted)/predicted,
                 ci95_halfwidth_s=float(student_t.ppf(.975,19)*se),
                 replications=20,customers_per_run=150000,warmup_customers=10000))
    with (out/'results.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    rawdir=Path('results/raw/queue-validation');rawdir.mkdir(parents=True,exist_ok=True)
    with (rawdir/'replications.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(raw[0]));writer.writeheader();writer.writerows(raw)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6.4,4.2),layout='constrained')
    for cv,label in [(0,'Deterministic service'),(1,'Exponential service')]:
        subset=[r for r in rows if r['service_cv']==cv]
        rho=[r['rho'] for r in subset]
        ax.plot(rho,[r['predicted_s']*1000 for r in subset],label=label+' analytical')
        ax.errorbar(rho,[r['simulated_mean_s']*1000 for r in subset],
          yerr=[r['ci95_halfwidth_s']*1000 for r in subset],fmt='o',capsize=3,label=label+' simulation')
    ax.set(xlabel='Verification utilization',ylabel='Mean sojourn time (ms)',
           title='Synthetic queue implementation check')
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    Path('figures').mkdir(exist_ok=True);fig.savefig('figures/queue-validation.png',dpi=180);plt.close(fig)
    report=dict(purpose='Synthetic implementation check with Poisson arrivals; no physical validation',
         worst_relative_error=max(r['relative_error'] for r in rows),
         all_within_10_percent=all(r['relative_error']<.1 for r in rows),
         historical_baseline_example_s=muhammad2019_mean(10,10,.001,.0001,.0005,.009))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if not report['all_within_10_percent']:raise SystemExit(1)


if __name__=='__main__':main()
