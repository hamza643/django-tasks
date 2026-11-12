import numpy as np

from .llm import embed
from .models import Chunk



def chunk_text(text: str, target_size: int = 500) -> list[str]:
    """Split on blank lines, then merge paragraphs up to about target_size characters."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) > target_size:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def cosine_similarity(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def ranked_chunks(question: str) -> list:
    """Every chunk with its score, best first: a list of (score, chunk) pairs."""
    question_vector = embed(question)
    scored = [
        (cosine_similarity(question_vector, chunk.embedding), chunk)
        for chunk in Chunk.objects.select_related("document").all()
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored


def top_chunks(question: str, k: int = 3) -> list:
    return [chunk for _score, chunk in ranked_chunks(question)[:k]]