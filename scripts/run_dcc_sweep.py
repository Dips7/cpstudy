"""Run DCC across the verification stress sweep."""
from pathlib import Path
import json
import numpy as np

from cpstudy.closed_loop import ClosedLoop
from cpstudy.config import validate

def main():
    out_base = Path("results/raw/major_revision")
    v_list = [1.0, 3.0, 6.0, 7.5, 10.0]
    seeds = [1, 2, 3]

    dcc_results = []
    for v in v_list:
        succs, lats, q_drops, exps, supps = [], [], [], [], []
        for s in seeds:
            cfg_dict = {
                "scenario": "intersection",
                "sources": 48,
                "verify_ms": v,
                "policy": "dcc",
                "duration_s": 5.0,
                "warmup_s": 1.0,
                "output": str(out_base / f"stress_v{int(v*10)}_dcc_s{s}")
            }
            cfg = validate(cfg_dict)
            rd = Path(cfg["output"])
            cl = ClosedLoop(cfg, s)
            cl.run_radio(rd)
            cl.run()
            res = cl.summary()
            (rd / "summary.json").write_text(json.dumps(res, indent=2))
            
            term = res.get("terminal_counts", {})
            succs.append(res.get("opportunity_success_rate", 0.0))
            if res.get("mean_success_latency_ms"):
                lats.append(res["mean_success_latency_ms"])
            q_drops.append(term.get("queue_overflow", 0))
            exps.append(term.get("verification_expired", 0) + term.get("fusion_expired", 0))
            supps.append(term.get("suppressed", 0))

        m_succ = float(np.mean(succs))
        s_succ = float(np.std(succs, ddof=1)) if len(succs) > 1 else 0.0
        m_lat = float(np.mean(lats)) if lats else None
        m_drop = float(np.mean(q_drops))
        m_exp = float(np.mean(exps))
        m_supp = float(np.mean(supps))

        rec = {
            "verify_ms": v,
            "policy": "dcc",
            "mean_succ": m_succ,
            "std_succ": s_succ,
            "mean_lat": m_lat,
            "mean_q_drop": m_drop,
            "mean_expired": m_exp,
            "mean_supp": m_supp
        }
        dcc_results.append(rec)
        lat_str = f"{m_lat:.2f} ms" if m_lat is not None else "None"
        print(f"DCC @ {v} ms: succ={m_succ*100:.2f}% (std {s_succ*100:.2f}%), lat={lat_str}, supp={m_supp:.1f}, drop={m_drop:.1f}, exp={m_exp:.1f}", flush=True)

    out_file = out_base / "dcc_stress_sweep.json"
    out_file.write_text(json.dumps(dcc_results, indent=2))
    print(f"Saved DCC stress sweep to {out_file}")

if __name__ == "__main__":
    main()
