"""Reproducible one-command demonstration."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .replay import decision_replay
from .investigator import investigate


def main():
    parser = argparse.ArgumentParser(description="DataPulse AI — silent semantic drift impact replay")
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    result, predictions = decision_replay(n=args.rows, seed=args.seed)
    report = investigate(result)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "replay_summary.json").write_text(json.dumps(result, indent=2))
    (out / "incident_report.json").write_text(json.dumps(report, indent=2))
    predictions.to_csv(out / "prediction_replay.csv", index=False)
    print(json.dumps({"prediction_flips": result["prediction_flips"],
                      "baseline_auc": result["baseline_model"]["roc_auc"],
                      "changed_auc": result["changed_data_same_model"]["roc_auc"],
                      "root_cause_hypothesis": report["incident_type"],
                      "artifact_directory": str(out)}, indent=2))


if __name__ == "__main__":
    main()
