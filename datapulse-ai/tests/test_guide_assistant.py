from pathlib import Path

import pytest

from datapulse.guide_assistant import (
    answer_guide, build_guide_messages, knowledge_chunks, retrieve_guidance
)
from datapulse.investigator import investigate
from datapulse.replay import decision_replay


def test_guide_has_project_documentation():
    chunks = knowledge_chunks()
    assert len(chunks) > 5
    assert any(x["source"] == "docs/DATAPULSE_USER_GUIDE.md" for x in chunks)


def test_retrieval_source_and_relevant_topic():
    hits = retrieve_guidance("Why does schema validation miss semantic drift?")
    assert hits
    assert all(h["source"].endswith(".md") and h["score"] > 0 for h in hits)


def test_fallback_truthfully_labeled():
    answer = answer_guide("What is DataPulse?")
    assert answer["mode"] == "retrieval_only"
    assert "RETRIEVAL-ONLY" in answer["answer"]
    assert answer["sources"]


def test_incident_prompt_contains_verified_report():
    summary, _ = decision_replay(n=500)
    report = investigate(summary)
    messages, hits = build_guide_messages("Why did the model change?", report=report)
    assert "prediction_flips" in messages[1]["content"]
    assert "incident_type" in messages[1]["content"]
    assert hits


def test_retrieval_rejects_invalid_questions():
    with pytest.raises(ValueError):
        retrieve_guidance("")
