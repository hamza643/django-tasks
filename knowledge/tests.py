from unittest.mock import patch

import requests

from django.test import TestCase

from .models import Chunk, Document
from .qa import answer_question



def fake_embed(text: str) -> list:
    """3 fake numbers: 'task' text points one way, everything else another."""
    return [1.0, 0.0, 0.0] if "task" in text.lower() else [0.0, 1.0, 0.0]


class RetrievalTests(TestCase):
    def setUp(self):
        notes = Document.objects.create(title="task_notes.md")
        Chunk.objects.create(document=notes, text="A Comment belongs to a Task.", embedding=[1.0, 0.0, 0.0])
        food = Document.objects.create(title="food.md")
        Chunk.objects.create(document=food, text="Biryani needs rice.", embedding=[0.0, 1.0, 0.0])

    @patch("knowledge.retrieval.embed", side_effect=fake_embed)
    def test_retrieval_finds_the_right_chunk(self, mock_embed):
        from .retrieval import top_chunks

        results = top_chunks("What does a task comment belong to?", k=1)
        self.assertEqual(results[0].document.title, "task_notes.md")

    @patch("knowledge.qa.generate", return_value="  A Comment belongs to a Task.  ")
    @patch("knowledge.retrieval.embed", side_effect=fake_embed)
    def test_answer_question_returns_answer_and_source(self, mock_embed, mock_generate):
        result = answer_question("What is a task comment?", k=1)
        self.assertEqual(result["answer"], "A Comment belongs to a Task.")
        self.assertEqual(result["sources"], ["task_notes.md"])
        prompt = mock_generate.call_args[0][0]
        self.assertIn("A Comment belongs to a Task.", prompt)

        

class AskViewTests(TestCase):
    def test_missing_question_gives_400(self):
        response = self.client.get("/ask/")
        self.assertEqual(response.status_code, 400)

    @patch(
        "knowledge.views.answer_question",
        return_value={"answer": "Because of caching.", "sources": ["docker-handout.md"]},
    )
    def test_ask_returns_answer_and_sources(self, mock_answer):
        response = self.client.get("/ask/", {"q": "Why copy requirements first?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Because of caching.")
        self.assertEqual(response.json()["sources"], ["docker-handout.md"])

    @patch("knowledge.views.answer_question", side_effect=requests.ConnectionError)
    def test_model_down_gives_503(self, mock_answer):
        response = self.client.get("/ask/", {"q": "anything"})
        self.assertEqual(response.status_code, 503)