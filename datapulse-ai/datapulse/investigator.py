"""Evidence-first root-cause diagnostics; LLM is optional, never source of metrics."""
from __future__ import annotations
import json


def investigate(summary: dict) -> dict:
    if not summary["schema_checks_after"]["passed"]:
        cause = "Technical schema or value quality failure"
        action = "Quarantine failed records and investigate the source contract."
    elif not summary["semantic_after"]["passed"]:
        cause = "Likely semantic definition change in engagement_events_30d"
        action = "Hold affected feature refresh; compare producer definitions and replay from a trusted snapshot after human approval."
    elif summary["drift"]["psi"] > 0.2:
        cause = "Feature distribution shift; root cause not yet established"
        action = "Investigate upstream changes and measure model behavior before deciding on intervention."
    else:
        cause = "No incident detected by configured monitors"
        action = "Continue monitoring; review model labels when available."
    return {
        "incident_type": cause,
        "evidence": {
            "schema_check_passed": summary["schema_checks_after"]["passed"],
            "semantic_discrepancy_rate": summary["semantic_after"]["discrepancy_rate"],
            "population_stability_index": summary["drift"]["psi"],
            "prediction_flips": summary["prediction_flips"],
            "false_negatives_before": summary["baseline_model"]["false_negatives"],
            "false_negatives_after": summary["changed_data_same_model"]["false_negatives"],
        },
        "recommended_action": action,
        "requires_human_approval": True,
        "limitations": summary["caveat"],
    }


def optional_gemini_explanation(report: dict, model_name: str = "gemini-3.8-flash") -> str:
    """Calls Gemini only with explicit configured credentials; not needed for core demo.

    Use GOOGLE_API_KEY in a private runtime, never commit secrets or generated credentials.
    No autonomous database writes or changes to production resources are permitted.
    """
    import os
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not configured. Run deterministic investigator offline instead.")
    from google import genai
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    prompt = ("You are a read-only data incident assistant. Summarize ONLY the JSON evidence. "
              "Do not invent values or claim causation. Include caveats and request human approval.\n" + json.dumps(report, sort_keys=True))
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text or "No text returned"
