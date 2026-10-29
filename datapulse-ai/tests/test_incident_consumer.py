import json
import pytest
from cloud.incident_consumer import parse_incident


GOOD = {"event_type":"ML_DATA_SEMANTIC_DRIFT", "source":"synthetic",
        "prediction_flips":12, "semantic_discrepancy_rate":0.7,
        "created_at":"2026-10-30T10:00:00+00:00"}


def test_parse_valid_message():
    result = parse_incident(json.dumps(GOOD).encode())
    assert result["prediction_flips"] == 12


@pytest.mark.parametrize("payload", [
    b"not-json",
    b"{}",
    json.dumps({**GOOD, "source":"production"}).encode(),
    json.dumps({**GOOD, "prediction_flips":True}).encode(),
    json.dumps({**GOOD, "prediction_flips":-1}).encode(),
    json.dumps({**GOOD, "semantic_discrepancy_rate":2}).encode(),
    json.dumps({**GOOD, "created_at":"not-a-date"}).encode(),
])
def test_parse_rejects_invalid_messages(payload):
    with pytest.raises(ValueError):
        parse_incident(payload)
