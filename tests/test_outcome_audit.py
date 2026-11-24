import csv
import gzip
import json

import pytest
from scripts.audit_outcomes import audit_run


def write_gzip_csv(path, fields, records):
    with gzip.open(path, "wt", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def write_events(path, records):
    with gzip.open(path, "wt") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")


def test_outcome_audit_separates_suppression_and_generated_terminals(tmp_path):
    write_gzip_csv(
        tmp_path / "network-opportunities.csv.gz",
        ["source_id", "sequence", "acquisition_ns", "deadline_ns", "generated", "receiver_ids"],
        [
            dict(source_id=0, sequence=0, acquisition_ns=0, deadline_ns=100,
                 generated=1, receiver_ids="1|2"),
            dict(source_id=0, sequence=1, acquisition_ns=10, deadline_ns=110,
                 generated=0, receiver_ids="1"),
        ],
    )
    write_events(tmp_path / "events.jsonl.gz", [
        dict(event_type="terminal", source_id=0, opportunity_id="0:0",
             receiver_id=1, reason="success"),
        dict(event_type="terminal", source_id=0, opportunity_id="0:0",
             receiver_id=2, reason="radio_not_received"),
        # Feedback uses no source opportunity identity and is ignored.
        dict(event_type="terminal", source_id=0, opportunity_id="feedback:8",
             receiver_id=1, reason="feedback_ready"),
    ])
    (tmp_path / "summary.json").write_text(json.dumps({
        "generated_receiver_pairs": 2,
        "terminal_counts": {"success": 1, "radio_not_received": 1},
    }))

    result = audit_run(tmp_path, duration_s=1, warmup_s=0)
    assert result["evaluated_demand_pairs"] == 3
    assert result["evaluated_suppressed_pairs"] == 1
    assert result["evaluated_generated_pairs"] == 2
    assert result["evaluated_terminal_reasons"] == {
        "success": 1, "radio_not_received": 1
    }
    assert all(result["conservation"].values())


def test_outcome_audit_rejects_duplicate_terminal_events(tmp_path):
    write_gzip_csv(
        tmp_path / "network-opportunities.csv.gz",
        ["source_id", "sequence", "acquisition_ns", "deadline_ns", "generated", "receiver_ids"],
        [dict(source_id=0, sequence=0, acquisition_ns=0, deadline_ns=100,
              generated=1, receiver_ids="1")],
    )
    duplicate = dict(event_type="terminal", source_id=0, opportunity_id="0:0",
                     receiver_id=1, reason="success")
    write_events(tmp_path / "events.jsonl.gz", [duplicate, duplicate])
    with pytest.raises(ValueError, match="duplicate terminal"):
        audit_run(tmp_path, duration_s=1, warmup_s=0)


def test_opportunity_with_no_eligible_receivers_is_valid(tmp_path):
    write_gzip_csv(
        tmp_path / "network-opportunities.csv.gz",
        ["source_id", "sequence", "acquisition_ns", "deadline_ns", "generated", "receiver_ids"],
        [dict(source_id=0, sequence=0, acquisition_ns=0, deadline_ns=100,
              generated=1, receiver_ids="")],
    )
    write_events(tmp_path / "events.jsonl.gz", [])
    result = audit_run(tmp_path, duration_s=1, warmup_s=0)
    assert result["evaluated_demand_pairs"] == 0
    assert all(result["conservation"].values())
