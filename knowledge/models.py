from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    embedding = models.JSONField()  # a plain list of floats, straight from Ollama

    def __str__(self):
        return self.text[:60]