"""OPTIONAL Gemini call on Vertex AI. This can incur charges."""
import argparse
from aegis.retrieval import search_policies,draft_evidence_prompt,ask_vertex_gemini
from aegis.risk import decision_replay


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-id',required=True)
    parser.add_argument('--confirm-billing',action='store_true')
    args=parser.parse_args()
    q='What happens if a laptop shipment is delayed by seven days, and which supplier escalation steps apply?'
    docs=search_policies(q)
    prompt=draft_evidence_prompt(q,docs,decision_replay())
    print('Retrieved sources:',[x['source'] for x in docs])
    if not args.confirm_billing:
        print('Cost-safe preview only. Pass --confirm-billing to call Vertex AI.')
        print(prompt[:1800]);return
    print(ask_vertex_gemini(prompt,args.project_id))

if __name__=='__main__':main()
