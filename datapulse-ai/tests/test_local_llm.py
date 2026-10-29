import pytest

from datapulse.local_llm import build_incident_messages, explain_deterministic
from datapulse.replay import decision_replay
from datapulse.investigator import investigate


def _report():
    summary, _ = decision_replay(n=500)
    return investigate(summary)


def test_local_prompt_contains_verified_incident():
    report = _report()
    messages = build_incident_messages(report)
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert report["incident_type"] in messages[1]["content"]


def test_local_explainer_requires_valid_report():
    with pytest.raises(ValueError):
        build_incident_messages({"evidence": {}})


def test_local_offline_fallback_is_labeled_and_grounded():
    report = _report()
    text = explain_deterministic(report)
    assert "NOT an LLM response" in text
    assert report["incident_type"] in text
    assert "Human approval required: True" in text
