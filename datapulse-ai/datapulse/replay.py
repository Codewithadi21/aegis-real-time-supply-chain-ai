"""Quantify decisions changed by a silent source semantic shift."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .generator import make_customer_data, introduce_semantic_shift
from .quality import validate_contract
from .model import split_customers, fit_baseline, score, metrics
from .drift import feature_checks, semantic_contract


def decision_replay(n: int = 5000, seed: int = 42, threshold: float = 0.5, retention_contact_cost: float = 200.0) -> tuple[dict, pd.DataFrame]:
    source = make_customer_data(n=n, seed=seed)
    changed = introduce_semantic_shift(source)
    train_ids, test_ids = split_customers(source)
    model = fit_baseline(source, train_ids)
    before = score(model, source, test_ids, threshold=threshold)
    after = score(model, changed, test_ids, threshold=threshold)
    compare = before[["customer_id", "churned_next_30d", "predicted_churn", "predicted_churn_probability"]].merge(
        after[["customer_id", "predicted_churn", "predicted_churn_probability"]],
        on="customer_id", validate="one_to_one", suffixes=("_before", "_after"))
    compare["decision_changed"] = compare.predicted_churn_before != compare.predicted_churn_after
    compare["missed_high_risk_after"] = (compare.churned_next_30d == 1) & (compare.predicted_churn_after == 0)
    # Model outputs are not business outcomes; this is only a contact-cost scenario.
    before_contacts = int(compare.predicted_churn_before.sum())
    after_contacts = int(compare.predicted_churn_after.sum())
    summary = {
        "dataset": "synthetic_customer_churn",
        "source_rows": int(len(source)), "test_rows": int(len(compare)),
        "schema_checks_before": validate_contract(source),
        "schema_checks_after": validate_contract(changed),
        "semantic_before": semantic_contract(source),
        "semantic_after": semantic_contract(changed),
        "drift": feature_checks(source, changed, "engagement_events_30d"),
        "baseline_model": metrics(before),
        "changed_data_same_model": metrics(after),
        "prediction_flips": int(compare.decision_changed.sum()),
        "prediction_flip_rate": round(float(compare.decision_changed.mean()), 4),
        "baseline_retention_contacts": before_contacts,
        "changed_retention_contacts": after_contacts,
        "hypothetical_contact_budget_difference_inr": round((after_contacts-before_contacts)*retention_contact_cost, 2),
        "caveat": "A paired replay detects prediction sensitivity, not causal business harm. Labels are synthetic; contact budget is illustrative, not realized revenue.",
    }
    return summary, compare
