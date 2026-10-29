"""Deterministic synthetic customer-risk data and controlled source breakages."""
from __future__ import annotations
import numpy as np
import pandas as pd

COUNTRIES = ("India", "United States", "United Kingdom", "Singapore")


def make_customer_data(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    if n < 100:
        raise ValueError("n must be at least 100 for a meaningful ML comparison")
    rng = np.random.default_rng(seed)
    purchases = rng.poisson(4, n)
    support = rng.poisson(1.5, n)
    tenure = rng.integers(1, 72, n)
    spend = np.maximum(0, purchases * rng.normal(700, 145, n) + rng.normal(220, 120, n))
    country = rng.choice(COUNTRIES, n)
    # Lower true purchases + frequent support problems -> greater churn probability.
    logit = 1.7 - 0.62 * purchases + 0.38 * support - 0.014 * tenure - 0.00015 * spend
    probability = 1 / (1 + np.exp(-logit))
    churn = rng.binomial(1, probability)
    return pd.DataFrame({
        "customer_id": [f"C{i:06d}" for i in range(n)],
        "country": country,
        "purchases_30d": purchases.astype(int),
        "engagement_events_30d": purchases.astype(int),  # contract: purchases, NOT logins
        "support_tickets_30d": support.astype(int),
        "tenure_months": tenure.astype(int),
        "spend_30d": np.round(spend, 2),
        "churned_next_30d": churn.astype(int),
    })


def introduce_semantic_shift(df: pd.DataFrame, seed: int = 73) -> pd.DataFrame:
    """Silent source definition change: engagement now counts login events.

    Same schema, same null constraints, integer and range; values remain plausible.
    Synthetic ground truth and other columns remain unchanged for paired replay.
    """
    rng = np.random.default_rng(seed)
    changed = df.copy(deep=True)
    # Common logins 5-12/week, weak correlation to actual purchases.
    logins = rng.poisson(16, len(changed))
    changed["engagement_events_30d"] = np.clip(logins, 0, 60).astype(int)
    return changed


def introduce_formatting_faults(df: pd.DataFrame) -> pd.DataFrame:
    """Whitespace, non-breaking space, and duplicates: detectable pipeline failures."""
    damaged = df.copy(deep=True)
    damaged.loc[damaged.index[0], "country"] = " India "
    damaged.loc[damaged.index[1], "country"] = "United\u00a0States"
    return pd.concat([damaged, damaged.iloc[[2]]], ignore_index=True)
