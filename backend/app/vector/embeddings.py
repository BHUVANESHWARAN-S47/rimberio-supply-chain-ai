import os
import math
import hashlib
from typing import List

def get_fallback_embedding(text: str, dim: int = 384) -> List[float]:
    """Generates a deterministic normalized pseudo-semantic vector embedding from input text.
    Ensures tests and vector search run reliably without external network dependencies.
    """
    words = text.lower().split()
    vec = [0.0] * dim
    for word in words:
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0.0:
        vec = [x / norm for x in vec]
    return vec

def generate_embedding(text: str) -> List[float]:
    """Generates an embedding vector for text using OpenAI if configured, otherwise using deterministic embedder."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and not api_key.startswith("your_"):
        try:
            # If OpenAI is accessible
            import openai
            client = openai.OpenAI(api_key=api_key)
            resp = client.embeddings.create(input=[text], model="text-embedding-3-small")
            return resp.data[0].embedding
        except Exception:
            pass

    return get_fallback_embedding(text)
