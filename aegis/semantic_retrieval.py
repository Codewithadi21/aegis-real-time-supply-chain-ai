"""OPTIONAL neural embeddings: mini transformer downloads weights on first run.
For an entirely offline demonstration use TF-IDF retrieval in aegis.retrieval.
"""
from pathlib import Path
import numpy as np

def semantic_search(question, policy_dir='policies', top_k=2):
    from sentence_transformers import SentenceTransformer
    files=sorted(Path(policy_dir).glob('*.md'))
    docs=[p.read_text(encoding='utf8') for p in files]
    if not docs:raise FileNotFoundError('No policy docs')
    model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeds=model.encode(docs,normalize_embeddings=True)
    q=model.encode([question],normalize_embeddings=True)[0]
    scores=embeds @ q
    idx=np.argsort(scores)[::-1][:top_k]
    return [{'source':files[i].name,'score':float(scores[i]),'text':docs[i]} for i in idx]
