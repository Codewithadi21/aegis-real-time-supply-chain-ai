import numpy as np
from datapulse.generator import make_customer_data, introduce_semantic_shift, introduce_formatting_faults
from datapulse.quality import validate_contract, clean_formatting
from datapulse.drift import semantic_contract, psi
from datapulse.replay import decision_replay
from datapulse.investigator import investigate


def test_generator_reproducible():
    a = make_customer_data(500, seed=7)
    b = make_customer_data(500, seed=7)
    assert a.equals(b)


def test_clean_contract():
    assert validate_contract(make_customer_data(300))["passed"]


def test_semantic_shift_passes_basic_contract():
    original = make_customer_data(300)
    shifted = introduce_semantic_shift(original)
    assert validate_contract(shifted)["passed"]
    assert semantic_contract(original)["passed"]
    assert not semantic_contract(shifted)["passed"]


def test_formatting_faults_detect_and_resolve():
    damaged = introduce_formatting_faults(make_customer_data(300))
    assert not validate_contract(damaged)["passed"]
    cleaned = clean_formatting(damaged)
    assert validate_contract(cleaned)["passed"]
    assert cleaned.loc[0, "country"] == "India"
    assert cleaned.loc[1, "country"] == "United States"


def test_psi_equal_zero():
    values = np.arange(150)
    assert abs(psi(values, values)) < 1e-8


def test_drift_detects_shift():
    original = make_customer_data(500)
    shifted = introduce_semantic_shift(original)
    assert psi(original.engagement_events_30d, shifted.engagement_events_30d) > 0.2


def test_replay_paired_cohort_and_prediction_changes():
    result, comparisons = decision_replay(n=1500)
    assert len(comparisons) == result["test_rows"]
    assert comparisons.customer_id.is_unique
    assert result["prediction_flips"] > 0
    assert result["schema_checks_after"]["passed"]


def test_replay_deterministic():
    a, _ = decision_replay(n=500, seed=9)
    b, _ = decision_replay(n=500, seed=9)
    assert a == b


def test_investigation_evidence_based():
    result, _ = decision_replay(n=500)
    report = investigate(result)
    assert report["requires_human_approval"]
    assert report["evidence"]["prediction_flips"] == result["prediction_flips"]
    assert "semantic" in report["incident_type"].lower()
