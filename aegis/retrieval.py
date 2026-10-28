"""Low-cost retrieval demo. TF-IDF is lexical vector retrieval, not neural embeddings."""
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def search_policies(question: str, policy_dir: str | Path='policies', top_k=2):
    files=sorted(Path(policy_dir).glob('*.md'))
    if not files:
        raise FileNotFoundError(f'No policy markdown files in {policy_dir}')
    docs=[p.read_text(encoding='utf8') for p in files]
    matrix=TfidfVectorizer(stop_words='english').fit_transform(docs+[question])
    similarities=cosine_similarity(matrix[-1],matrix[:-1]).flatten()
    top=sorted(range(len(files)), key=lambda i:similarities[i], reverse=True)[:top_k]
    return [{'source':files[i].name,'score':round(float(similarities[i]),3), 'text':docs[i]} for i in top]


def draft_evidence_prompt(question: str, retrieved: list[dict], scenario_data: list[dict]):
    context='\n\n'.join(f"[{x['source']}]\n{x['text']}" for x in retrieved)
    return ("You are an electronics operations analyst. Answer ONLY using the scenario numbers and "
            "supplier policy excerpts below. Cite the bracketed policy filename for policy claims. "
            "State that revenue exposure is a hypothetical scenario and never claim a guaranteed loss. "
            "If evidence is missing, say so.\n\n"
            f"Question: {question}\nScenario results: {scenario_data}\nPolicy excerpts:\n{context}")


def ask_vertex_gemini(prompt: str, project_id: str, model: str='gemini-2.5-flash'):
    """OPTIONAL paid API; call only intentionally, after checking account/model access."""
    from google import genai
    client=genai.Client(vertexai=True,project=project_id,location='global')
    response=client.models.generate_content(model=model,contents=prompt)
    return response.text
