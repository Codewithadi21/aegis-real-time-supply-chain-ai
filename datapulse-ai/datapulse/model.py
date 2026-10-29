"""Baseline churn model. Fixed cohort and fixed model enable controlled replay."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, recall_score, precision_score, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["engagement_events_30d", "support_tickets_30d", "tenure_months", "spend_30d"]
TARGET = "churned_next_30d"


def split_customers(df: pd.DataFrame, seed: int = 19):
    """Stable ID-based split; replay must use identical test customers."""
    train_ids, test_ids = train_test_split(df["customer_id"].tolist(), test_size=0.3, random_state=seed, stratify=df[TARGET].tolist())
    return set(train_ids), set(test_ids)


def fit_baseline(df: pd.DataFrame, train_ids: set[str]):
    rows = df[df.customer_id.isin(train_ids)]
    pipeline = Pipeline([("scale", StandardScaler()), ("model", LogisticRegression(max_iter=1500, random_state=42))])
    pipeline.fit(rows[FEATURES], rows[TARGET])
    return pipeline


def score(model, frame: pd.DataFrame, test_ids: set[str], threshold: float = 0.5) -> pd.DataFrame:
    rows = frame[frame.customer_id.isin(test_ids)].copy().sort_values("customer_id")
    rows["predicted_churn_probability"] = model.predict_proba(rows[FEATURES])[:, 1]
    rows["predicted_churn"] = (rows["predicted_churn_probability"] >= threshold).astype(int)
    return rows


def metrics(scored: pd.DataFrame) -> dict:
    truth = scored[TARGET].to_numpy()
    predicted = scored["predicted_churn"].to_numpy()
    cm = confusion_matrix(truth, predicted, labels=[0, 1])
    return {
        "rows": int(len(scored)),
        "positive_rate": round(float(np.mean(truth)), 4),
        "roc_auc": round(float(roc_auc_score(truth, scored["predicted_churn_probability"])), 4),
        "recall": round(float(recall_score(truth, predicted, zero_division=0)), 4),
        "precision": round(float(precision_score(truth, predicted, zero_division=0)), 4),
        "accuracy": round(float(accuracy_score(truth, predicted)), 4),
        "false_negatives": int(cm[1, 0]),
        "false_positives": int(cm[0, 1]),
    }
