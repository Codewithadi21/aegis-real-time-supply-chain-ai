"""Run the full offline demonstrator before creating billable cloud resources."""
from pathlib import Path
import json
import pandas as pd
from aegis.synthetic import generate
from aegis.events import new_sale,validate_sale
from aegis.risk import decision_replay
from aegis.retrieval import search_policies,draft_evidence_prompt


def run():
    frames=generate()
    print('Synthetic reference datasets:',{k:len(v) for k,v in frames.items()})
    event=validate_sale(new_sale())
    print('Example event:',json.dumps(event,indent=2))
    cases=decision_replay()
    print('\nSupply Chain Decision Replay:')
    print(pd.DataFrame(cases).to_string(index=False))
    question='What happens if a laptop supplier shipment is delayed seven days and which escalation rule applies?'
    found=search_policies(question)
    print('\nPolicy evidence:',[(r['source'],r['score']) for r in found])
    print('\nGrounded Gemini prompt preview (no API called):\n',draft_evidence_prompt(question,found,cases)[:700],'...')
    print('\nSUCCESS: Offline demo complete. Next: Colab + GCP.')

if __name__=='__main__':run()
