from .llm import build_prompt, generate
from .retrieval import top_chunks


def answer_question(question: str, k: int = 3) -> dict:
    """Retrieve the best chunks, ask the model, return the answer and its sources."""
    chunks = top_chunks(question, k)
    answer = generate(build_prompt(question, chunks))
    sources = sorted({chunk.document.title for chunk in chunks})
    return {"answer": answer.strip(), "sources": sources}