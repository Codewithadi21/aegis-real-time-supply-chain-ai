"""Distribution and semantic monitoring: not all drift indicates model harm."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


def psi(reference, current, n_bins: int = 10) -> float:
    """Population Stability Index on reference quantile bins, epsilon guarded."""
    a = np.asarray(reference, dtype=float)
    b = np.asarray(current, dtype=float)
    edges = np.unique(np.quantile(a, np.linspace(0, 1, n_bins + 1)))
    if len(edges) < 2:
        return 0.0 if np.allclose(a.mean(), b.mean()) else float("inf")
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.histogram(a, bins=edges)[0] / len(a)
    q = np.histogram(b, bins=edges)[0] / len(b)
    epsilon = 1e-6
    return float(np.sum((q - p) * np.log((q + epsilon) / (p + epsilon))))


def feature_checks(reference: pd.DataFrame, current: pd.DataFrame, feature: str) -> dict:
    a = reference[feature].to_numpy(dtype=float)
    b = current[feature].to_numpy(dtype=float)
    ks = ks_2samp(a, b)
    return {"feature": feature, "baseline_mean": round(float(a.mean()), 3),
            "changed_mean": round(float(b.mean()), 3),
            "psi": round(psi(a, b), 4), "ks_statistic": round(float(ks.statistic), 4),
            "ks_pvalue": round(float(ks.pvalue), 6)}


def semantic_contract(frame: pd.DataFrame) -> dict:
    """Domain truth: engagement_events_30d should represent purchase activity.

    This check is only possible when an independent trusted proxy is available;
    it illustrates why a documented semantic contract matters.
    """
    differences = frame["engagement_events_30d"] - frame["purchases_30d"]
    discrepancy = float((differences != 0).mean())
    return {"metric": "engagement_matches_purchases", "discrepancy_rate": round(discrepancy, 4),
            "passed": discrepancy <= 0.01}
