import requests


def embed(text: str) -> list:
    response = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "nomic-embed-text", "input": text},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]

def generate(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"]


def build_prompt(question: str, chunks) -> str:
    facts = "\n".join(f"{i + 1}. {chunk.text}" for i, chunk in enumerate(chunks))
    return (
        "Answer the question using ONLY the facts listed below. "
        "If the facts do not say, say you do not know.\n\n"
        f"Facts:\n{facts}\n\n"
        f"Question: {question}\n\n"
        "Answer in one or two short sentences."
    )