from pathlib import Path

from django.core.management.base import BaseCommand

from knowledge.llm import embed
from knowledge.models import Chunk, Document
from knowledge.retrieval import chunk_text


class Command(BaseCommand):
    help = "Read every .txt/.md file in a folder, chunk it, embed each chunk, and store it."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str)

    def handle(self, *args, **options):
        folder = Path(options["folder"])
        files = sorted(list(folder.glob("*.txt")) + list(folder.glob("*.md")))
        for path in files:
            document, _ = Document.objects.get_or_create(title=path.name)
            document.chunks.all().delete()  # re-ingesting replaces old chunks
            pieces = chunk_text(path.read_text(encoding="utf-8"))
            for piece in pieces:
                Chunk.objects.create(document=document, text=piece, embedding=embed(piece))
            self.stdout.write(self.style.SUCCESS(f"{path.name}: {len(pieces)} chunks"))