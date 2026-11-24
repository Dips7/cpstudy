from pathlib import Path
import hashlib
import json
import math
import yaml

DEFAULTS = {
    "schema_version": 1, "scenario": "intersection", "sources": 10,
    "duration_s": 10.0, "warmup_s": 2.0, "opportunity_hz": 10.0,
    "max_rate_hz": 10.0, "min_rate_hz": 1.0, "deadline_ms": 100.0,
    "inference_ms": 10.0, "sign_ms": 1.0, "verify_ms": 1.0,
    "fusion_ms": 2.0, "queue_capacity": 32, "payload_bytes": 1100,
    "security_bytes": 100, "policy": "fixed", "control_ms": 100.0,
    "feedback_stale_ms": 300.0, "feedback_bytes": 96,
    "radio_high": 0.65, "radio_low": 0.4,
    "queue_high": 8, "queue_low": 2, "decrease": 0.8, "increase_hz": 0.5,
    "radio": "ideal", "ideal_delay_ms": 1.0, "output": "results/raw/pilot",
    "service_cv": 0.0, "clock_offset_ms": 0.0,
    "feedback_ms": 200.0, "range_m": 150.0, "speed_mps": 10.0,
    "matched_feedback": False,
}


def validate(c):
    if not all(isinstance(k,str) for k in c):
        raise ValueError("Configuration keys must be strings")
    unknown = set(c) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
    c = DEFAULTS | c
    for k, v in c.items():
        if isinstance(DEFAULTS[k],bool) and not isinstance(v,bool):
            raise ValueError(f"{k} must be boolean")
        if not isinstance(DEFAULTS[k],bool) and isinstance(DEFAULTS[k],(int,float)) and (not isinstance(v,(int,float)) or isinstance(v,bool)):
            raise ValueError(f"{k} must be numeric")
        if isinstance(DEFAULTS[k],str) and not isinstance(v,str):
            raise ValueError(f"{k} must be a string")
        if isinstance(v, (float, int)) and not math.isfinite(v):
            raise ValueError(f"Nonfinite parameter: {k}")
    if c["schema_version"] != 1:
        raise ValueError("Unsupported schema_version")
    if not isinstance(c["sources"], int) or isinstance(c["sources"], bool) or c["sources"] < 2:
        raise ValueError("sources must be an integer >= 2")
    for k in ("queue_capacity", "payload_bytes", "security_bytes", "feedback_bytes"):
        if not isinstance(c[k], int) or isinstance(c[k], bool) or c[k] < 0:
            raise ValueError(f"{k} must be a nonnegative integer")
    for k in ("duration_s", "opportunity_hz", "deadline_ms", "control_ms", "feedback_stale_ms", "feedback_ms", "range_m", "speed_mps"):
        if c[k] <= 0:
            raise ValueError(f"{k} must be positive")
    for k in ("inference_ms", "sign_ms", "verify_ms", "fusion_ms", "ideal_delay_ms", "service_cv"):
        if c[k] < 0:
            raise ValueError(f"{k} cannot be negative")
    if not 0 <= c["warmup_s"] < c["duration_s"] - c["deadline_ms"] / 1000:
        raise ValueError("Evaluation window must contain observable deadlines")
    if not 0 < c["min_rate_hz"] <= c["max_rate_hz"] <= c["opportunity_hz"]:
        raise ValueError("Require 0 < min <= max <= opportunity rate")
    if c["policy"] not in ("fixed", "radio", "receiver", "joint", "calibrated", "dcc"):
        raise ValueError("Unknown policy")
    if c["scenario"] not in ("intersection", "highway", "static-pilot"):
        raise ValueError("Unknown scenario")
    if c["radio"] not in ("ideal", "ns3", "ns3-closed-loop"):
        raise ValueError("Unknown radio backend")
    if not 0 <= c["radio_low"] < c["radio_high"] <= 1:
        raise ValueError("Invalid radio thresholds")
    if not 0 <= c["queue_low"] < c["queue_high"]:
        raise ValueError("Invalid queue thresholds")
    if not 0 < c["decrease"] < 1 or c["increase_hz"] <= 0:
        raise ValueError("Invalid controller gains")
    if c['policy']=='dcc' and (c['min_rate_hz']!=1 or c['matched_feedback'] or c['control_ms']!=100):
        raise ValueError('DCC reference requires 1 Hz minimum, 100 ms sampling, and no added feedback service')
    return c


def load(path):
    value = yaml.safe_load(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError("Configuration must be a mapping")
    return validate(value)


def digest(c):
    # Output location is operational, not a scientific parameter.
    return hashlib.sha256(json.dumps({k:v for k,v in c.items() if k != "output"},
                                   sort_keys=True).encode()).hexdigest()
