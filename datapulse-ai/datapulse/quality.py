"""Basic data-contract checks and optional safe canonicalization."""
from __future__ import annotations
import re
import unicodedata
import pandas as pd

REQUIRED = {
    "customer_id", "country", "purchases_30d", "engagement_events_30d",
    "support_tickets_30d", "tenure_months", "spend_30d", "churned_next_30d",
}
NUMERIC_NONNEGATIVE = ("purchases_30d", "engagement_events_30d", "support_tickets_30d", "tenure_months", "spend_30d")


def normalize_category(s: object) -> str:
    v = unicodedata.normalize("NFKC", str(s)).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", v).strip()


def validate_contract(frame: pd.DataFrame, *, strict_keys: bool = True) -> dict:
    missing = sorted(REQUIRED - set(frame.columns))
    issues: list[str] = []
    if missing:
        return {"passed": False, "issues": [f"Missing columns: {', '.join(missing)}"], "row_count": len(frame)}
    if frame[list(REQUIRED)].isna().any().any():
        issues.append("Nulls in required fields")
    if strict_keys and frame["customer_id"].duplicated().any():
        issues.append("Duplicate customer IDs")
    if frame["customer_id"].astype(str).str.strip().eq("").any():
        issues.append("Blank customer IDs")
    for col in NUMERIC_NONNEGATIVE:
        x = pd.to_numeric(frame[col], errors="coerce")
        if x.isna().any() or (x < 0).any():
            issues.append(f"Invalid nonnegative numeric: {col}")
    if not frame["churned_next_30d"].isin([0, 1]).all():
        issues.append("Invalid binary outcome")
    return {"passed": not issues, "issues": issues, "row_count": len(frame)}


def clean_formatting(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy(deep=True)
    result["country"] = result["country"].map(normalize_category)
    return result.drop_duplicates(subset=["customer_id"], keep="first").reset_index(drop=True)
